from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json

from .payments_common import ORDER_TABLE, PAYMENTS_TABLE, CURRENCY_TABLE, LOG_TABLE, SUBSCRIBE_TABLE

from .liqpay_api import LP
bank = 'liqpay'
lp = LP()

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
                query = f'INSERT INTO {LOG_TABLE} (app_id, "type", data) VALUES (%s, %s, %s)'
                cursor.execute(query, [app_id, bank, json.dumps(response, ensure_ascii=False),])

                query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
                cursor.execute(query, [json.dumps(response, ensure_ascii=False), response.get('order_id')])

                cursor.execute(PAYMENTS_QUERY, [response.get('order_id'),])

        return HttpResponse()


class PaymentLiqpayView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        with connections['pcnt'].cursor() as cursor:
            query = f'''SELECT amount, currency, description, periodicity, app_id FROM {ORDER_TABLE} WHERE order_id=%s AND "type"='{bank}';'''
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            app_id = row[4]
            if not app_id in lp.app_ids.values():
                return Response({'error': f'{app_id} has no {bank} params'}, status=status.HTTP_400_BAD_REQUEST)

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
