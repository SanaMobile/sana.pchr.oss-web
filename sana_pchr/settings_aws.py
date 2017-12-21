from sana_pchr.settings_base import *

"""
Django settings for sana_pchr project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# Default to use Postgres. Update values.
DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST':  '127.0.0.1',
                'PORT': '5432',
        }
}

ADMINS = (('', ''),)

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''

DEBUG=True
