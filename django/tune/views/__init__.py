from .crud import *

import os
import environ
environ.Env.read_env()

TUNE_API_KEY=os.environ.get('TUNE_API_KEY', 'Xa-xa-xa')
TUNE_BASE_URL=os.environ.get('TUNE_BASE_URL', 'Xa-xa-xa')
TUNE_KID=os.environ.get('TUNE_KID', 'Xa-xa-xa')

from .jwt_HS256 import JWT_HS256
jwt_worker = JWT_HS256(TUNE_KID)

from .img_server import *

