from rest_framework.response import Response
from rest_framework import status

from django.db import connections
import json

from pcnt.base import PCNTBaseAPIView

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
