from django.conf import settings
import requests

class Userfront():
    error = ''
    def __init__(self, user):
        try:
            self.token = "Bearer " + settings.TENANTIDS[user.tenant_id][user.mode]
            self.site = settings.TENANTIDS[user.tenant_id]['site']
        except Exception as err:
            self.error = 'User credentials missed or not configured'
            return

        self.roles_url = f'https://api.userfront.com/v0/tenants/{user.tenant_id}/users/{user.id}/roles'
        self.users_url = f'https://api.userfront.com/v0/tenants/{user.tenant_id}/users/{user.id}'

        self.headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": self.site,
            "Authorization": self.token
        }

    def put_request(self, url, data):
        try:
            response = requests.put(url, headers=self.headers, json=data)
        except Exception as err:
            return str(err)
        if response.status_code != 200:
            return f'Error request: {url}'
        return 'Ok'

    def set_roles(self, roles):
        result = self.put_request(self.roles_url, {"roles": roles})
        return result

    def set_custom_data(self, data):
        result = self.put_request(self.users_url, {"data": data})
        return result
