from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connections
from django.utils.html import escape  # for sanitizing 'func' input
import json

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
