import os
import sys

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://*.paradim.science', 'https://*.ulaval.ca']

if sys.argv[1] in ['makemigrations', 'collectstatic']:
    SECRET_KEY = 'django-insecure-x0qyxi-n@9ko*cjpth)gd78b_d+l*u9z^!gq-7o4a68i1x-c&@'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
else:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    DATABASES = {
        'default': {
            'ENGINE': os.environ['DATABASE_ENGINE'],
            'NAME': os.environ['DATABASE_NAME'],
            'USER': os.environ['DATABASE_USERNAME'],
            'PASSWORD': os.environ['DATABASE_PASSWORD'],
            'HOST': os.environ['DATABASE_HOST'],
            'PORT': os.environ['DATABASE_PORT'],
        }
    }
