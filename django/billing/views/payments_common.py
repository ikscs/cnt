from django.http import HttpResponse
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json

import environ
environ.Env.read_env()

ORDER_TABLE = 'billing.orders'
PAYMENTS_TABLE = 'billing.payments'
CURRENCY_TABLE = 'billing.currency'
LOG_TABLE = 'billing.callback_log'

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
