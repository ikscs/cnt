import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class UserfrontJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')
        if not auth:
            return None

        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            raise AuthenticationFailed('Invalid Authorization header format.')

        token = parts[1]
        try:
            # Replace with your actual Userfront public key
            payload = jwt.decode(token, settings.USERFRONT_PUBLIC_KEY['cnt'], algorithms=['RS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        return (payload, token)
