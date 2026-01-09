from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json
import copy

from .payments_common import ORDER_TABLE, PAYMENTS_TABLE, CURRENCY_TABLE, LOG_TABLE, SUBSCRIBE_TABLE

from .monobank_api import MB
bank = 'monobank'
mb = MB()

PAYMENTS_QUERY_MB = f'''INSERT INTO {PAYMENTS_TABLE} (order_id, bank_order_id, currency, amount, dt, type, app_id, customer_id, subscription_id)
SELECT o.order_id, o.data->>'invoiceId',
(SELECT name FROM {CURRENCY_TABLE} WHERE code=(o.data->>'ccy')::INTEGER),
((o.data->>'amount')::REAL/100)::numeric(20,2),
(o.data->>'modifiedDate')::TIMESTAMPTZ,
o.type, o.app_id, o.customer_id,
o.data->>'subscriptionId'
FROM {ORDER_TABLE} o
WHERE o.order_id = %s
AND o.data->>'status' IN ('success')
ON CONFLICT (order_id, bank_order_id) DO UPDATE SET
currency = EXCLUDED.currency,
amount = EXCLUDED.amount,
dt = EXCLUDED.dt,
type = EXCLUDED.type,
app_id = EXCLUDED.app_id,
customer_id  = EXCLUDED.customer_id,
subscription_id = EXCLUDED.subscription_id;'''

SUBSCRIBE_QUERY = f'''INSERT INTO {SUBSCRIBE_TABLE}
(customer_id, app_id, order_id, subscription_id, subscription_state, type, currency, amount, periodicity, dt_start_pay, dt_next_pay, data)
SELECT o.customer_id, o.app_id, o.order_id,
%s, %s, o.type,
(SELECT COALESCE(name, 'unknown') FROM {CURRENCY_TABLE} WHERE code=%s),
(%s)::numeric(20,2),
%s,%s,%s,%s
FROM orders o
WHERE o.order_id = %s
ON CONFLICT (customer_id) DO UPDATE SET
app_id = EXCLUDED.app_id,
order_id = EXCLUDED.order_id,
subscription_id = EXCLUDED.subscription_id,
subscription_state = EXCLUDED.subscription_state,
type = EXCLUDED.type,
currency = EXCLUDED.currency,
amount = EXCLUDED.amount,
periodicity = EXCLUDED.periodicity,
dt_start_pay = EXCLUDED.dt_start_pay,
dt_next_pay = EXCLUDED.dt_next_pay,
data = EXCLUDED.data;
'''

@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackViewMB(View):
    def post(self, request, *args, **kwargs):
        app_id = request.GET.get('app_id')
        if not app_id:
            return HttpResponse()
        if not app_id in mb.app_ids.values():
            return HttpResponse()

        data = request.body
        signature = request.headers.get('X-Sign')

        if not data or not signature:
            return HttpResponse()

        if mb.verify_signature(app_id, data, signature):
            try:
                decoded_string = request.body.decode('utf-8')
                response = json.loads(decoded_string)
            except Exception as err:
                print(str(err))
                response = {}
            with connections['pcnt'].cursor() as cursor:
                query = f'INSERT INTO {LOG_TABLE} (app_id, "type", data) VALUES (%s, %s, %s)'
                cursor.execute(query, [app_id, bank, json.dumps(response, ensure_ascii=False),])

                subscription_id = response.get('subscriptionId')
                invoice_id = response.get('invoiceId')

                if subscription_id:
                    query = f'''SELECT order_id FROM {ORDER_TABLE} WHERE app_id=%s AND "type"=%s AND (data->>'subscriptionId')::TEXT=%s;'''
                    cursor.execute(query, [app_id, bank, subscription_id,])
                    row = cursor.fetchone()
                    if not row:
                        order_id = 0
                    else:
                        order_id = row[0]
                else:
                    order_id = response.get('reference')
                    try:
                        order_id = int(order_id)
                    except Exception as err:
                        order_id = 0

                status = response.get('status')
                if status in ('success', 'failure', 'reversed', 'expired'):
                    query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
                    cursor.execute(query, [json.dumps(response, ensure_ascii=False), order_id,])

                if status in ('success',):
                    cursor.execute(PAYMENTS_QUERY_MB, [order_id, ])

                if status in ('active', 'cancelled') and subscription_id:
                    amount = response.get('amount', 0)/100

                    periodicity = {'1d': 'day', '1w': 'week', '1m': 'month', '1y': 'year'}.get(response.get('interval'), response.get('interval', 'unknown'))
                    start_dt = response.get('startDate')
                    next_dt = response.get('nextChargeDate')

                    cursor.execute(SUBSCRIBE_QUERY, [subscription_id, status, response.get('ccy'), amount, periodicity, start_dt, next_dt, json.dumps(response, ensure_ascii=False), order_id])

        return HttpResponse()

class PaymentMonobankView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'''SELECT amount, (SELECT code FROM {CURRENCY_TABLE} WHERE name=currency) AS currency_code, description, periodicity, app_id, (data->>'pageUrl')::TEXT FROM {ORDER_TABLE} WHERE order_id=%s AND "type"='{bank}';'''
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            app_id = row[4]
            if not app_id in mb.app_ids.values():
                return Response({'error': f'{app_id} has no {bank} params'}, status=status.HTTP_400_BAD_REQUEST)

            amount = int(round(float(row[0])*100))
            currency = row[1]
            description = row[2]
            periodicity = row[3]
            link = row[5]

            if not amount or not currency or not description:
                return Response({'error': f'Order {order_id} invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if not link:
            params = copy.deepcopy(mb.params[app_id])

            params['amount'] = amount
            params['ccy'] = currency
            params['merchantPaymInfo']['reference'] = str(order_id)
            params['merchantPaymInfo']['destination'] = description

            if periodicity:
                params['interval'] = {'day': '1d', 'week': '1w', 'month': '1m', 'year': '1y'}.get(periodicity, '1m')
                url = mb.subscribe_url
            else:
                url = mb.invoice_url

            result = mb.post_request(url, mb.cfg[app_id]['TOKEN'], params)
            try:
                link = result['pageUrl']
            except Exception as err:
                return Response({'error': f'Cannot process order {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            with connections['pcnt'].cursor() as cursor:
                query = f'''UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s AND "type"='{bank}';'''
                cursor.execute(query, [json.dumps(result, ensure_ascii=False), order_id,])

        html = f'''<html><head><meta http-equiv="refresh" content="0; url={link}"><title>Redirecting...</title></head>
<body>
<p>If you are not redirected automatically, follow this <a href="{link}">link</a>.</p>
</body></html>'''

        return HttpResponse(html)
