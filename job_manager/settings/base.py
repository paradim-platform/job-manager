import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rest_framework.reverse import reverse_lazy

load_dotenv('.env')

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'manager.apps.ManagerConfig',
    'dispatcher.apps.DispatcherConfig',
    'launcher.apps.LauncherConfig',
    'drf_spectacular',
    'drf_spectacular_sidecar',  # required for Django collectstatic discovery
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'job_manage_cache',
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'job_manager.middleware.azure_ad_middleware',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'job-management-api',
    'DESCRIPTION': 'Service that exposes jobs data',
    'VERSION': None,
    'REDOC_DIST': 'SIDECAR',
}

ROOT_URLCONF = 'job_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'job_manager.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] [{module}] [{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOGGING_LEVEL,
    },
}

# Avoid needing env variables when collecting static files
if sys.argv[1] not in ['collectstatic']:
    # Celery stuff
    CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']

    CELERY_TIMEZONE = TIME_ZONE
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60
    CELERY_WORKER_CONCURRENCY = 1
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

    # For Azure AD OAuth
    OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
    OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
    OAUTH_TENANT_ID = os.environ['OAUTH_TENANT_ID']
    OAUTH_REDIRECT_URL = os.environ['OAUTH_REDIRECT_URL']
    OAUTH_AUTHORITY_URL = f'https://login.microsoftonline.com/{OAUTH_TENANT_ID}'

    # For Kheops
    KHEOPS_URL = os.environ['KHEOPS_URL']
    KHEOPS_API_URL = os.environ['KHEOPS_API_URL']

JAZZMIN_SETTINGS = {
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Cache", "url": reverse_lazy('admin-cache-management'), "new_window": True},
    ],
}
