# middleware/db_session_init.py

from django.db import connection

class SetAppRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            customer_id = getattr(user, 'customer_id', None)
            if customer_id:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SET ROLE app_user;")
                        cursor.execute("SET app.customer_id = %s;", [str(customer_id)])
#                        cursor.execute("call wr_log('qq');")
                except Exception as err:
                    print(str(err))

        return response
