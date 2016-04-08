"""
Django settings for wanglibao_sso project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-g0t3p(o9=m6z2*3j3vupythz0i!e)p7mvld!@6(m1&@t4tgnz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # third part apps
    'south',
    'mama_cas',

    # my apps
    'wanglibao_accounts',
    'wanglibao_profile',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Authentication backend
AUTHENTICATION_BACKENDS = (
    'wanglibao_accounts.auth_backends.EmailPhoneUsernameAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'wanglibao_sso.urls'

WSGI_APPLICATION = 'wanglibao_sso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'wanglibao/mysql.cnf'),
        }
    },
}

if 1:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wanglibao',
        'USER': 'wanglibao',
        'PASSWORD': 'wanglibank',
        #'HOST': '192.168.1.242',
    }


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MAMA_CAS_ALLOW_AUTH_WARN = True
MAMA_CAS_ASYNC_CONCURRENCY = 2
MAMA_CAS_FOLLOW_LOGOUT_URL = True
MAMA_CAS_TICKET_EXPIRE = 9000000
MAMA_CAS_TICKET_RAND_LEN = 32
MAMA_CAS_VALID_SERVICES = ()
# MAMA_CAS_ATTRIBUTE_CALLBACKS = ('callbacks.user_token_attributes',)
MAMA_CAS_ATTRIBUTE_CALLBACKS = ('zgxcw_sso.callbacks.user_token_attributes',)
MAMA_CAS_ENABLE_SINGLE_SIGN_OUT = True
