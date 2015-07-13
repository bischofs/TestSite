"""
Django settings for TestSite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c+rlxx%mmvg38gc@^%pq09#q*5u=m7ofq892s$15s2ag!5cna-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    '172.26.1.87',
    'compute01.fev.com',
    'localhost',
    '127.0.0.1',
]


AUTH_USER_MODEL = 'Authentication.Account'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django_python3_ldap',
    'djangular',
    'Authentication',
    'Project',
    'Ebench',
    'rest_framework',
    'compressor',
    'simple_history',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
  #  'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'TestSite.middleware.DisableCSRF'
)

ROOT_URLCONF = 'TestSite.urls'

WSGI_APPLICATION = 'TestSite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'django_db',
        'USER': 'root',
        'PASSWORD':'mazdarx7'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
      #'djangular.finders.NamespacedAngularAppDirectoriesFinder'
)

STATIC_URL = '/1065/static/'

STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)


REST_FRAMEWORK = {
     'DEFAULT_PERMISSION_CLASSES': [
         'rest_framework.permissions.AllowAny'
     ]
}

AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",)


# The URL of the LDAP server.
LDAP_AUTH_URL = "ldap://usw001.fev.com:389"

# The LDAP search base for looking up users.
LDAP_AUTH_SEARCH_BASE = "ou=US,ou=User Accounts,dc=FEV,dc=COM"

# The LDAP class that represents a user.
LDAP_AUTH_OBJECT_CLASS = "Person"

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# A tuple of fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# Callable that transforms the user data loaded from
# LDAP into a form suitable for creating a user.
# Override this to set custom field formatting for your
# user model.
from django_python3_ldap import utils
LDAP_AUTH_CLEAN_USER_DATA = utils.clean_user_data

LOGGING = {
    'version': 1,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        }
    },
}
