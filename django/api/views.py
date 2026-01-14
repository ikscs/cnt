from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.db import connections
from django.utils.html import escape  # for sanitizing 'func' input
import json
import uuid

'''
class CallDbFunctionView(APIView):
    def post(self, request):
        func = request.query_params.get("func")

        if not func:
            return Response({"error": "Missing 'func' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            escaped_func = escape(func)  # basic sanitization
            input_data = json.dumps(request.data)

            with connections['pcnt'].cursor() as cursor:
                query = f"SELECT {escaped_func}(%s);"
                cursor.execute(query, [input_data])
                rows = cursor.fetchall()

            result = [json.loads(row[0]) for row in rows]
            return Response(*result, content_type='application/json')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''

class HelloView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, JWT Authenticated User!"})

class UnsubscribeView(APIView):
    def is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    def get(self, request):
        uuid = request.query_params.get('uuid')

        if not uuid:
            result = 'Missing subscribe uuid'
        elif not self.is_valid_uuid(uuid):
            result = 'Wrong uuid'
        else:
            result = 'Unsubscrebe succesefull'
            try:
                with connections['pcnt'].cursor() as cursor:
                    query = 'UPDATE public.customer_ext SET email_enabled=false WHERE unsubscribe_uuid=%s;'
                    cursor.execute(query, [uuid,])
            except Exception as err:
                result = 'Something goes wrong'

        data = f'''<!DOCTYPE html>
<html>
<head>
  <title>Unsubscribe</title>
  <meta charset="utf-8">
</head>
<body>
  <h1>{result}</h1>
</body>
</html>'''
        return HttpResponse(data)
