import os
from .base import *


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['try-deploy-django.com', '34.91.108.195']

CSRF_TRUSTED_ORIGINS = ['https://try-deploy-django.com']
CSRT_COOKIE_SECURE = True

STATIC_URL = '/static/'
STATIC_ROOT = '/demo/www/public'
