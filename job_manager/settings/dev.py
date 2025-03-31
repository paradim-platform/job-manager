from .base import *  # noqa: F403

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x0qyxi-n@9ko*cjpth)gd78b_d+l*u9z^!gq-7o4a68i1x-c&@'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

