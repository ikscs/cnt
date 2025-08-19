from django.conf import settings
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

from pcnt.base import PCNTBaseViewSet, PCNTBaseAPIView, PCNTBaseReadOnlyViewSet

from liqpay import LiqPay

liqpay_params = {
    'action': 'pay',
    'amount': '0.01',
    'currency': 'USD',
    'description': '',
    'order_id': 0,
    'version': '3',
    'sandbox': settings.LIQPAY['SANDBOX'],
    'server_url': settings.LIQPAY['CALLBACK'],
}
if settings.LIQPAY.get('RESULT_URL'):
    liqpay_params['result_url'] = settings.LIQPAY['RESULT_URL']

ORDER_TABLE = 'billing.orders'

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
        params = liqpay_params

        rows = []
        field_names = []
        with connections['pcnt'].cursor() as cursor:
            query = f'SELECT order_id, amount, currency, description, data FROM {ORDER_TABLE};'
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
                    for e in ['order_id', 'amount', 'currency', 'description']:
                        params[e] = str(row[e])
                    signature = liqpay.cnb_signature(params)
                    data = liqpay.cnb_data(params)

                    form_html = f'''
<a href="/api/billing/pay_liqpay/?order_id={row['order_id']}" target="_blank">Pay Now</a>
<form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8">
<input type="hidden" name="data" value="{data}">
<input type="hidden" name="signature" value="{signature}">
<input type="submit" value="Pay Now">
</form>
<a href="/api/billing/pay_status/?order_id={row['order_id']}">Check status</a>
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
        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY['PRIVATE_KEY'] + data + settings.LIQPAY['PRIVATE_KEY'])
        response = liqpay.decode_data_from_str(data)
        if sign == signature:
            with connections['pcnt'].cursor() as cursor:
                query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
                cursor.execute(query, [json.dumps(response), response.get('order_id')])
        return HttpResponse()

class PaymentLiqpayView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        field_names = []
        with connections['pcnt'].cursor() as cursor:
            query = f'SELECT amount, currency, description FROM {ORDER_TABLE} WHERE order_id=%s;'
            cursor.execute(query, [order_id,])

            row = cursor.fetchone()
            if not row:
                return Response({'error': f'Not found {order_id}'}, status=status.HTTP_400_BAD_REQUEST)

            amount = row[0]
            currency = row[1]
            description = row[2]

        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])
        params = liqpay_params
        params['amount'] = str(amount)
        params['currency'] = currency
        params['description'] = description
        params['order_id'] = str(order_id)

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

class PaymentStatusView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'error': 'Missing order_id'}, status=status.HTTP_400_BAD_REQUEST)

        liqpay = LiqPay(settings.LIQPAY['PUBLIC_KEY'], settings.LIQPAY['PRIVATE_KEY'])

        try:
            res = liqpay.api('request', {
                'action': 'status',
                'version': '3',
                'order_id': order_id,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with connections['pcnt'].cursor() as cursor:
            query = f'UPDATE {ORDER_TABLE} SET data=%s WHERE order_id=%s'
            cursor.execute(query, [json.dumps(res), order_id])

        return Response(res, status=status.HTTP_200_OK)

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
                cursor.execute(query, [amount, currency, description, app_id, user.tenant_id, user.id, user.mode, json.dumps(param)])
                row = cursor.fetchone()
                if not row or not row[0]:
                    return Response({'error': f'Order not created'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            order_id = row[0]

        data = {'order_id': order_id, 'amount': amount, 'currency': currency, 'description': description, 'app_id': app_id, 'param': param}
        return Response(data, status=status.HTTP_200_OK)
