"""
Django settings for Diplom project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT='C:/Users/Admin/PycharmProjects/Diplom/media/'
MEDIA_URL='/media/'

_PATH = os.path.abspath(os.path.dirname(__file__))
#
# MEDIA_ROOT = os.path.join(_PATH, 'files', 'media')
# MEDIA_URL = '/media/'
#
STATIC_ROOT = os.path.join(_PATH, 'files', 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(_PATH, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
#
# ADMIN_MEDIA_PREFIX = '/static/admin/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'afonderkin@gmail.com'
EMAIL_HOST_PASSWORD = 'rtyujhgf'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k-pud+@r4be9e(-tv48(%by4)+s^zfaky774ual6jrtfrlw(k+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# TEMPLATE_CONTEXT_PROCESSORS = (
#   'django.core.context_processors.request',
# )

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'PlaningSystem',
    'django.contrib.admin',
    'registration',
    'south'
)

ACCOUNT_ACTIVATION_DAYS = 2
AUTH_USER_EMAIL_UNIQUE = True
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False
# DEFAULT_FROM_EMAIL = 'info@google.ru'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'Diplom.urls'

AUTH_USER_MODEL = 'PlaningSystem.User'

WSGI_APPLICATION = 'Diplom.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request")