import os

from .base import *

DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wa10ry&+mkywslsux+p50p=%d$)el1og6^nxsrlz2r0$(s+6(-'


# For development server django-debug-toolbar
_INTERNAL_IPS = ['127.0.0.1', "localhost"]
INTERNAL_IPS = _INTERNAL_IPS
ALLOWED_HOSTS = _INTERNAL_IPS

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.joinpath('db.sqlite3'),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASS")

STRIPE_PUBLIC_KEY = "pk_test_A7jK4iCYHL045qgjjfzAfPxu"  # pass into view context
STRIPE_SECRET_KEY = "sk_test_Hrs6SAopgFPF0bZXSN3f6ELN"  # set to stripe.api_key
