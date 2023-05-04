import os
from .base import *
from google.oauth2 import service_account

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['try-deploy-django.com', '34.81.108.195']

CSRF_TRUSTED_ORIGINS = ['https://try-deploy-django.com']
CSRT_COOKIE_SECURE = True

STATIC_URL = '/static/'
STATIC_ROOT = '/demo/www/public'

## For media store in the bucket
## Getting credential
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(os.path.join(BASE_DIR, 'credential.json'))

##configuration for media file storing and retriving media file from gcloud
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'try-deploy-django-bucket'
MEDIA_URL = 'https://storage.googleapis.com/try-deploy-django-bucket/'
