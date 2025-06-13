import jwt
import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings

USERFRONT_PUBLIC_KEYS_URL = f'https://api.userfront.com/v0/tenants/{settings.TENANTID}/keys/jwt'
public_key = requests.get(USERFRONT_PUBLIC_KEYS_URL).json()['results'][0]['publicKey']

class UserfrontAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                options={"verify_aud": False}
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(f'Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

        if payload['tenantId'] != settings.TENANTID:
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
