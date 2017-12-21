"""
Django settings for sana_pchr project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

import dj_database_url

from sana_pchr.settings_base import *
from sana_pchr.settings_sms import *
from sana_pchr.settings_update import *

ADMINS = [('', '')]

EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
EMAIL_PORT = 587

DEBUG = False

SERVER_EMAIL = ''

DATABASES = {'default': dj_database_url.config()}
