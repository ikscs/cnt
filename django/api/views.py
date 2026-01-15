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
    template = '''<!DOCTYPE html>
<html>
<head>
  <title>Unsubscribe</title>
  <meta charset="utf-8">
</head>
<body>
{}
</body>
</html>'''

    def is_valid_uuid(self, val):
        if not val:
            return False
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    def unsubscribe(self, uuid):
        try:
            with connections['pcnt'].cursor() as cursor:
                query = 'UPDATE public.customer_ext SET email_enabled=false WHERE unsubscribe_uuid=%s;'
                cursor.execute(query, [uuid,])
                result = '<h1>Unsubscrebe succesefull</h1>'
        except Exception as err:
            result = '<h1>Something goes wrong</h1>'
        return result

    def get(self, request):
        uuid = request.query_params.get('uuid')
        if not self.is_valid_uuid(uuid):
            result = '<h1>Wrong uuid</h1>'
        else:
            result = f'''Confirm unsubscribe
<form action="" method="POST">
  <input type="hidden" name="uuid" value="{uuid}">
  <input type="hidden" name="confirm" value="yes">
  <button type="submit">Confirm</button>
</form>'''

        data = self.template.format(result)

        return HttpResponse(data)

    def post(self, request):
        uuid = request.POST.get('uuid')
        confirm = request.POST.get('confirm')
        print(uuid, confirm)

        if confirm != 'yes':
            result = '<h1>Unsubscribe terminated</h1>'
        elif not self.is_valid_uuid(uuid):
            result = '<h1>Wrong uuid</h1>'
        else:
            result = self.unsubscribe(uuid)

        data = self.template.format(result)
        return HttpResponse(data)
