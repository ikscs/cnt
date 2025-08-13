from pathlib import Path
import environ
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

#Set False for product!
BYPASS_AUTH = False

USERFRONT_PUBLIC_KEY = {
#    "cnt": env('USERFRONT_PUBLIC_KEY_CNT'),
    "cnt": 'USERFRONT_PUBLIC_KEY_CNT',
}

TENANTIDS = dict()
for k, v in os.environ.items():
    if k.startswith('TENANT'):
        for k1, v1 in json.loads(v).items():
            TENANTIDS[k1] = v1

ALLOWED_HOSTS = ["*"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    "rest_framework",
    "rest_framework_simplejwt",
    "helloworld",
    "authdemo",
    "pcnt",
    "django_filters",
    "billing",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'pcnt.authentication.UserfrontAuthentication',
#        'rest_framework_simplejwt.authentication.JWTAuthentication',
#        'authdemo.authentication.UserfrontJWTAuthentication',
    ),
#    'DEFAULT_PERMISSION_CLASSES': [
#        'rest_framework.permissions.IsAuthenticated',
#    ],

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
#    'middleware.db_session_init.SetAppRoleMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "api.urls"

WSGI_APPLICATION = "api.wsgi.application"

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": BASE_DIR / "db.sqlite3",
#    }
#}

#2do: Remove it
PCNT_DATABASE = env.db('PCNT_DATABASE_URL')
if 'billing' not in PCNT_DATABASE['OPTIONS']['options']:
    PCNT_DATABASE['OPTIONS']['options'] += ',billing'

DATABASES = {
    'default': env.db('DATABASE_URL'),
    'sqlite': env.db('SQLITE_DATABASE_URL'),
    'pcnt': PCNT_DATABASE,
#     'pcnt': env.db('PCNT_DATABASE_URL')
}

DATABASE_ROUTERS = ['api.dbrouters.PcntRouter']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#FORCE_SCRIPT_NAME = '/api'

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / 'staticfiles'

environ.Env.read_env(os.path.join(BASE_DIR, 'billing', '.env'))
LIQPAY = dict()
for k, v in os.environ.items():
    if k.startswith('LIQPAY_'):
        k = k.split('_', 1)[-1]
        LIQPAY[k] = v

TIME_ZONE = 'Europe/Kyiv'
USE_TZ = True
