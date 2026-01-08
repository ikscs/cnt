from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json
import copy

from pcnt.base import PCNTBaseViewSet, PCNTBaseAPIView, PCNTBaseReadOnlyViewSet

import environ
environ.Env.read_env()

from .liqpay_api import LP
from .monobank_api import MB

lp = LP()
mb = MB()

ORDER_TABLE = 'billing.orders'
PAYMENTS_TABLE = 'billing.payments'

PAYMENTS_QUERY = f'''INSERT INTO {PAYMENTS_TABLE} (order_id, bank_order_id, currency, amount, dt, type, app_id, customer_id, subscription_id)
SELECT  o.order_id, COALESCE(o.data->>'liqpay_order_id', ''), o.data->>'currency', (o.data->>'amount')::numeric,
to_timestamp((o.data->>'end_date')::double precision / 1000.0),
o.type, o.app_id, o.customer_id,
CASE
  WHEN (o.data->>'action')::TEXT = 'pay' THEN NULL
  ELSE o.data->>'action'
END
FROM {ORDER_TABLE} o
WHERE o.order_id = %s
AND o.data->>'status' IN ('success', 'subscribed', 'sandbox')
AND o.data->>'action' IN ('pay', 'subscribe', 'regular')
ON CONFLICT (order_id, bank_order_id) DO UPDATE SET
currency = EXCLUDED.currency,
amount = EXCLUDED.amount,
dt = EXCLUDED.dt,
type = EXCLUDED.type,
app_id = EXCLUDED.app_id,
customer_id  = EXCLUDED.customer_id,
subscription_id = EXCLUDED.subscription_id;'''


PAYMENTS_QUERY_MB = f'''INSERT INTO {PAYMENTS_TABLE} (order_id, bank_order_id, currency, amount, dt, type, app_id, customer_id, subscription_id)
SELECT o.order_id, o.data->>'invoiceId',
(SELECT name FROM billing.currency WHERE code=(o.data->>'ccy')::INTEGER),
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


class PayView(View):
    header = '''<html><body><pre>
Картки для тестування
4242424242424242	Успішна оплата
4000000000003063	Успішна оплата з 3DS
4000000000003089	Успішна оплата з OTP
4000000000003055	Успішна оплата з CVV
4000000000000002	Не успішна оплата. Код помилки - limit
4000000000009995	Не успішна оплата. Код помилки - 9859
sandbox_token	Успішна оплата по токену
</pre><hr>'''
    footer = '</body></html>'

    def get(self, request, *args, **kwargs):
        rows = []
        field_names = []
        with connections['pcnt'].cursor() as cursor:
            query = f'SELECT order_id, amount, currency, description, data, app_id, "type" FROM {ORDER_TABLE} ORDER BY order_id;'
            cursor.execute(query)
            field_names = [e[0] for e in cursor.description]
            for row in cursor.fetchall():
                r = {name: value for name, value in zip(field_names, row)}
                rows.append(r)

        result = '<table border="1"><tr>'
        for name in field_names:
            result += f'<th>{name}</th>'
        result += '</tr>\n<tbody>'
        for row in rows:
            result += '<tr>'
            for k, v in row.items():
                if k == 'order_id':
                    form_html = f'''
<br><a href="/api/billing/pay_liqpay/?order_id={row['order_id']}" target="_blank">LiqPay</a>
<br><a href="/api/billing/pay_monobank/?order_id={row['order_id']}" target="_blank">MonoBank</a>
<br><br><a href="/api/billing/pay_status/?order_id={row['order_id']}">Check status</a>
'''
                    result += f'<td>{v}{form_html}</td>'
                else:
                    result += f'<td>{v}</td>'
            result += '</tr>'
        result += '</tbody></table>'

        return HttpResponse(f'{self.header}{result}{self.footer}')

@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackView(View):
    def post(self, request, *args, **kwargs):
        app_id = request.GET.get('app_id')
        if not app_id:
            return HttpResponse()
        if not app_id in lp.app_ids.values():
            return HttpResponse()

        data = request.POST.get('data')
        signature = request.POST.get('signature')
        if not data or not signature:
            return HttpResponse()

        liqpay = lp.mk_liqpay(app_id)
        sign = liqpay.str_to_sign(lp.cfg[app_id]['PRIVATE_KEY'] + data + lp.cfg[app_id]['PRIVATE_KEY'])
        if sign == signature:
            try:
                response = liqpay.decode_data_from_str(data)
            except Exception as err:
                response = {}
            with connections['pcnt'].cursor() as cursor:
                query = f'INSERT INTO billing.callback_log (app_id, "type", data) VALUES (%s, %s, %s)'
                cursor.execute(query, [app_id, 'liqpay', json.dumps(response, ensure_ascii=False),])

                query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
                cursor.execute(query, [json.dumps(response, ensure_ascii=False), response.get('order_id')])

                cursor.execute(PAYMENTS_QUERY, [response.get('order_id'),])

        return HttpResponse()

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
                query = f'INSERT INTO billing.callback_log (app_id, "type", data) VALUES (%s, %s, %s)'
                cursor.execute(query, [app_id, 'monobank', json.dumps(response, ensure_ascii=False),])

                subscription_id = response.get('subscriptionId')
                invoice_id = response.get('invoiceId')

                if subscription_id:
                    query = f'''SELECT order_id FROM {ORDER_TABLE} WHERE app_id=%s AND "type"=%s AND (data->>'subscriptionId')::TEXT=%s;'''
                    cursor.execute(query, [app_id, 'monobank', subscription_id,])
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

        return HttpResponse()

class PaymentLiqpayView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'''SELECT amount, currency, description, periodicity, app_id FROM {ORDER_TABLE} WHERE order_id=%s AND "type"='liqpay';'''
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            app_id = row[4]
            if not app_id in lp.app_ids.values():
                return Response({'error': f'{app_id} has no liqpay params'}, status=status.HTTP_400_BAD_REQUEST)

            amount = row[0]
            currency = row[1]
            description = row[2]
            periodicity = row[3]

        liqpay = lp.mk_liqpay(app_id)
        params = lp.params[app_id]
        params['amount'] = str(amount)
        params['currency'] = currency
        params['description'] = description
        params['order_id'] = str(order_id)

        if periodicity:
            params['action'] = 'subscribe'
            params['subscribe_date_start'] = '2025-01-01 00:00:00'
            params['subscribe_periodicity'] = periodicity
        else:
            params['action'] = 'pay'

        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_data(params)

        html = f'''
<html><body onload="document.forms[0].submit()">
<form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8">
<input type="hidden" name="data" value="{data}">
<input type="hidden" name="signature" value="{signature}">
<input type="submit" value="Pay Now">
</form>
</body></html>'''

        return HttpResponse(html)

class PaymentMonobankView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'''SELECT amount, (SELECT code FROM billing.currency WHERE name=currency) AS currency_code, description, periodicity, app_id, (data->>'pageUrl')::TEXT FROM {ORDER_TABLE} WHERE order_id=%s AND "type"='monobank';'''
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            app_id = row[4]
            if not app_id in mb.app_ids.values():
                return Response({'error': f'{app_id} has no monobank params'}, status=status.HTTP_400_BAD_REQUEST)

            amount = int(round(float(row[0])*100))
            currency = row[1]
            description = row[2]
            periodicity = row[3]
            link = row[4]

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
                query = f'''UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s AND "type"='monobank';'''
                cursor.execute(query, [json.dumps(result, ensure_ascii=False), order_id,])

        html = f'''<html><head><meta http-equiv="refresh" content="0; url={link}"><title>Redirecting...</title></head>
<body>
<p>If you are not redirected automatically, follow this <a href="{link}">link</a>.</p>
</body></html>'''

        return HttpResponse(html)

class PaymentStatusView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'''SELECT app_id, "type", (data->>'invoiceId')::TEXT FROM {ORDER_TABLE} WHERE order_id=%s'''
            cursor.execute(query, [order_id,])
            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)
            app_id = row[0]
            type_pay = row[1]
            invoice_id = row[2]

        if type_pay == 'liqpay':
            liqpay = lp.mk_liqpay(app_id)
            try:
                result = liqpay.api('request', {
                    'action': 'status',
                    'version': '3',
                    'order_id': order_id,
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif type_pay == 'monobank':
            if not invoice_id:
                return Response({'error': f'Order {order_id} has no invoiceId'}, status=status.HTTP_400_BAD_REQUEST)

            result = mb.get_request(f'{mb.status_url}{invoice_id}', mb.cfg[app_id]['TOKEN'])
            if not isinstance(result, dict):
                return Response({'error': str(result)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': f'Cannot check staus of order {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
            cursor.execute(query, [json.dumps(result, ensure_ascii=False), order_id])

            if type_pay == 'liqpay':
                cursor.execute(PAYMENTS_QUERY, [order_id,])
            elif type_pay == 'monobank':
                cursor.execute(PAYMENTS_QUERY_MB, [order_id,])

        return Response(result, status=status.HTTP_200_OK)

class PaymentResultView(View):
    def get(self, request, *args, **kwargs):
        data = '''<!DOCTYPE html>
<html>
<head>
  <title>Thank You!</title>
  <meta charset="utf-8">
</head>
<body>
  <h1>Дякуємо, що Ви з нами.</h1>
  Сторінку оплати можна закрити
</body>
</html>'''
        return HttpResponse(data)

from .models import Balance
from .serializers import BalanceSerializer
class BalanceViewSet(PCNTBaseViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

from .models import TestOrder
from .serializers import TestOrderSerializer
class TestOrderViewSet(viewsets.ModelViewSet):
    queryset = TestOrder.objects.all()
    serializer_class = TestOrderSerializer

from .models import SubscriptionBasePrice
from .serializers import SubscriptionBasePriceSerializer
class SubscriptionBasePriceViewSet(PCNTBaseReadOnlyViewSet):
    queryset = SubscriptionBasePrice.objects.all()
    serializer_class = SubscriptionBasePriceSerializer

from .models import Order
from .serializers import OrderSerializer
class OrderReadOnlyViewSet(PCNTBaseReadOnlyViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

from .models import CameraCategory
from .serializers import CameraCategorySerializer
class CameraCategoryReadOnlyViewSet(PCNTBaseReadOnlyViewSet):
    queryset = CameraCategory.objects.all()
    serializer_class = CameraCategorySerializer

class CreateLiqpayOrderView(PCNTBaseAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        amount = data.get('amount')
        currency = data.get('currency')
        description = data.get('description')
        app_id = data.get('app_id')
        param = data.get('param')

        if not all((amount, currency, description, app_id, not(param is None))):
            return Response({'error': 'Data incomplete'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        with connections['pcnt'].cursor() as cursor:
            query = f'SELECT * FROM billing.create_liqpay_order(%s, %s, %s, %s, %s, %s, %s, %s);'
            try:
                cursor.execute(query, [amount, currency, description, app_id, user.tenant_id, user.id, user.mode, json.dumps(param, ensure_ascii=False)])
                row = cursor.fetchone()
                if not row or not row[0]:
                    return Response({'error': f'Order not created'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            order_id = row[0]

        data = {'order_id': order_id, 'amount': amount, 'currency': currency, 'description': description, 'app_id': app_id, 'param': param}
        return Response(data, status=status.HTTP_200_OK)
