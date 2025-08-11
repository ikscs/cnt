from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json

from pcnt.base import PCNTBaseAPIView

from liqpay import LiqPay

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
        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])
        params = {
            'action': 'pay',
            'amount': '100',
            'currency': 'USD',
            'description': 'Payment for clothes',
            'order_id': 'order_id_6',
            'version': '3',
            'sandbox': settings.LIQPAY['SANDBOX'], # sandbox mode, set to 1 to enable it
            'server_url': settings.LIQPAY['CALLBACK'],
            'result_url': settings.LIQPAY['RESULT_URL'],
        }

        rows = []
        field_names = []
        with connections['pcnt'].cursor() as cursor:
            query = "SELECT order_id, amount, currency, description, result, status, data FROM billing.test_order;"
            cursor.execute(query)
            field_names = [e[0] for e in cursor.description]
            for row in cursor.fetchall():
                r = {name: value for name, value in zip(field_names, row)}
                rows.append(r)

        result = "<table border=\"1\"><tr>"
        for name in field_names:
            result += f"<th>{name}</th>"
        result += "</tr>\n<tbody>"
        for row in rows:
            result += "<tr>"
            for k, v in row.items():
                if k == 'order_id':
                    for e in ['order_id', 'amount', 'currency', 'description']:
                        params[e] = row[e]
                    signature = liqpay.cnb_signature(params)
                    data = liqpay.cnb_data(params)

                    form_html = f'''
<a href="/api/pay-liqpay/?order_id={row['order_id']}">Pay Now</a>
<form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8">
<input type="hidden" name="data" value="{data}">
<input type="hidden" name="signature" value="{signature}">
<input type="submit" value="Pay Now">
</form>
<a href="/api/payment-status/?order_id={row['order_id']}">Check status</a>
'''
                    result += f"<td>{v}{form_html}</td>"
                else:
                    result += f"<td>{v}</td>"
            result += "</tr>"
        result += "</tbody></table>"

        return HttpResponse(f'{self.header}{result}{self.footer}')

@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackView(View):
    def post(self, request, *args, **kwargs):
        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY['PRIVATE_KEY'] + data + settings.LIQPAY['PRIVATE_KEY'])
        response = liqpay.decode_data_from_str(data)
        print('callback data', response)
        if sign == signature:
            print('callback is valid')
            with connections['pcnt'].cursor() as cursor:
                query = f'UPDATE billing.test_order SET result=%s, status=%s, data=%s WHERE order_id=%s'
                cursor.execute(query, [response.get('result'), response.get('status'), json.dumps(response), response.get('order_id')])
        return HttpResponse()

class PaymentLiqpayView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        field_names = []
        with connections['pcnt'].cursor() as cursor:
            query = "SELECT amount, currency, description FROM billing.test_order WHERE order_id=%s;"
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            amount = row[0]
            currency = row[1]
            description = row[2]

        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])
        params = {
            'action': 'pay',
            'amount': amount,
            'currency': currency,
            'description': description,
            'order_id': order_id,
            'version': '3',
            'sandbox': settings.LIQPAY['SANDBOX'], # sandbox mode, set to 1 to enable it
            'server_url': settings.LIQPAY['CALLBACK'],
            'result_url': settings.LIQPAY['RESULT_URL'],
        }
        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_data(params)

        html = f'''
<html><body onload="document.forms[0].submit()">
<form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8">
<input type="hidden" name="data" value="{data}">
<input type="hidden" name="signature" value="{signature}">
</form>
</body></html>'''

        return Response(html, status=status.HTTP_200_OK)

class PaymentStatusView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])

        try:
            res = liqpay.api("request", {
                "action": "status",
                "version": "3",
                "order_id": order_id,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with connections['pcnt'].cursor() as cursor:
            query = f'UPDATE billing.test_order SET result=%s, status=%s, data=%s WHERE order_id=%s'
            cursor.execute(query, [res.get('result'), res.get('status'), json.dumps(res), order_id])

        return Response(res, status=status.HTTP_200_OK)

class PaymentResultView(APIView):
    def get(self, request, *args, **kwargs):
        data = {'result': 'After payment page'}
        return Response(data, status=status.HTTP_200_OK)
