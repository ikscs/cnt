import jwt
import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings

#Load public keys
public_key = dict()
USERFRONT_PUBLIC_KEYS_URL = 'https://api.userfront.com/v0/tenants/{tenant_id}/keys/jwt{param}'
for tenant_id in settings.TENANTIDS:
    public_key[tenant_id] = dict()
    for mode, param in {'live': '?live=true', 'test': '?test=true'}.items():
        url = USERFRONT_PUBLIC_KEYS_URL.format(tenant_id=tenant_id, param=param)
        public_key[tenant_id][mode] = requests.get(url).json()['results'][0]['publicKey']


class UserfrontAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
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

        user = FakeUser(payload['userId'], payload.get('userUuid'))
        return (user, None)

class FakeUser:
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username or f"user_{user_id}"
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
