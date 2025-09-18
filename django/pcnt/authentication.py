import jwt
import json
import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings
from django.db import connections

#Load public keys
public_key = dict()
USERFRONT_PUBLIC_KEYS_URL = 'https://api.userfront.com/v0/tenants/{tenant_id}/keys/jwt{param}'
for tenant_id in settings.TENANTIDS:
    public_key[tenant_id] = dict()
    for mode, param in {'live': '?live=true', 'test': '?test=true'}.items():
        url = USERFRONT_PUBLIC_KEYS_URL.format(tenant_id=tenant_id, param=param)
        public_key[tenant_id][mode] = requests.get(url).json()['results'][0]['publicKey']

import socket
import ipaddress

#Load local network
ip_address = socket.gethostbyname(socket.gethostname())
MY_NETWORK = ipaddress.ip_network(f'{ip_address}/16', strict=False)

def is_trusted_network(ip):
    return ipaddress.ip_address(ip) in MY_NETWORK

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class UserfrontAuthentication(BaseAuthentication):
    def authenticate(self, request):

        if settings.BYPASS_AUTH:
            user = AuthUser(None, None, 'Authentification disabled!!!')
            return (user, None)

        auth_header = request.headers.get('Authorization')
        if settings.DEBUG and auth_header and 'SuperMario' in auth_header:
            try:
                payload = json.loads(auth_header)
                user = AuthUser(payload['tenantId'], payload['userId'], payload.get('userUuid'), payload['mode'])
                return (user, None)
            except Exception as err:
                pass

        if auth_header and is_trusted_network(get_client_ip(request)):
            try:
                payload = json.loads(auth_header)
                user = AuthUser(payload.get('tenantId'), payload.get('userId'), payload.get('userUuid'), payload.get('mode'), payload.get('customer_id'))
                return (user, None)
            except Exception as err:
                pass

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        #Select public_key
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            pk = public_key[payload['tenantId']][payload['mode']]
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

        try:
            payload = jwt.decode(
                token,
                pk,
                algorithms=['RS256'],
                options={"verify_aud": False}
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(f'Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

        if payload['tenantId'] not in settings.TENANTIDS:
            raise AuthenticationFailed(f'Wrong tenantId')

        user = AuthUser(payload['tenantId'], payload['userId'], payload.get('userUuid'), payload['mode'])
        return (user, None)

class AuthUser:
    def __init__(self, tenant_id=None, user_id=None, username=None, mode=None, customer_id=None):
        self.id = user_id
        self.username = username or f"user_{user_id}"
        self.tenant_id = tenant_id
        self.mode = mode
        self.customer_id = customer_id

        with connections['pcnt'].cursor() as cursor:
            if self.customer_id == None:
                cursor.execute("CALL public.set_rls(%s, %s, %s);", [self.tenant_id, self.id, self.mode])
            else:
                cursor.execute("CALL public.set_customer_tz(%s); SET ROLE app_user; SET app.customer_id = %s;", [self.customer_id, self.customer_id,])

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
