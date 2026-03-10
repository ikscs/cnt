from django.conf import settings
import jwt
import datetime

class JWT_HS256():
    iss = 'aipeeper_app'

    def __init__(self, kid, ttl_minutes=60):
        self.kid = kid
        self.key = settings.SECRET_KEY
        self.ttl_minutes = ttl_minutes

    def mk_jwt(self, uuid):
        payload = {
            'iss': self.iss,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=self.ttl_minutes),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'uuid': uuid
        }
        encoded_jwt = jwt.encode(payload, self.key, algorithm="HS256", headers={"kid": self.kid},)
        return encoded_jwt

    def get_uuid(self, token):
        try:
            header = jwt.get_unverified_header(token)
        except Exception as err:
            return None

        if header.get('kid') != self.kid:
            return None

        try:
            payload = jwt.decode(token, self.key, algorithms=['HS256'], options={"verify_aud": False}, issuer=self.iss)
        except Exception as e:
            print(str(e))
            return None

        return payload.get('uuid')

if __name__ == "__main__":
    class X():
        SECRET_KEY = 'AAAAAA'
    settings = X()

    jwt_worker = JWT_HS256('ls1')

    uuid = '00083d32a83d4c0680d54d0fe98976c2'

    encoded_jwt = jwt_worker.mk_jwt(uuid)
    print("jwt:", encoded_jwt)

    z = jwt_worker.get_uuid(encoded_jwt)
    print("uuid:", z)
