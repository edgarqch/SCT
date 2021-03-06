"""
Django settings for sit project.

Generated by 'django-admin startproject' using Django 1.11.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.core.urlresolvers import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qsjmvd5r3@c1^(*@vfdvay87jexv0427(dffbjn#dog7km#w0u'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.101',
                '192.168.1.102',
                '192.168.1.103',
                '192.168.1.104',
                '192.168.1.105',
                '192.168.1.106',
                '192.168.1.107',
                '192.168.1.108',
                '192.168.1.109',
                '192.168.1.110',
                '192.168.1.111',
                '192.168.1.112',
                '192.168.1.113',
                '192.168.1.114',
                '192.168.1.115',
                'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.tramite',
    'apps.vehiculo',
    'apps.operario',
    'apps.tecnico',
    'apps.usuario',
    'ckeditor',
    'ckeditor_uploader',
    'preventconcurrentlogins',
    'axes',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware',
    'axes.middleware.FailedLoginMiddleware',
]
# Opciones disponibles para personalizar un poco los django-ejes . Estos deben ser definidos en su archivo settings.py .
import datetime as dt
delta = dt.timedelta(minutes=1)

AXES_LOGIN_FAILURE_LIMIT = 3 #El numero de intentos de inicio de sesion permitidos antes de que se cree un registro para los inicios de sesion fallidos.
AXES_LOCK_OUT_AT_FAILURE = True #Despues de que se exceda el numero de intentos de inicio de sesion permitidos, deberiamos bloquear esta IP (y el agente de usuario opcional)?
AXES_USE_USER_AGENT = True #Si es verdadero , bloquee / inicie sesion basandose en una direccion IP Y un agente de usuario. Esto significa que las solicitudes de diferentes agentes de usuario, pero de la misma IP se tratan de manera diferente.
AXES_COOLOFF_TIME = delta #Si se establece, define un periodo de inactividad despues del cual se olvidaran los intentos de inicio de sesion fallidos. Se puede establecer en un objeto timedelta de python o en un entero. Si es un entero, se interpretara como un numero de horas.
AXES_LOGGER = 'axes.watch_login' #Si se establece, especifica un mecanismo de registro para que lo utilicen los ejes.
AXES_LOCKOUT_URL = '/logout/' #Si esta configurado, especifica una URL para redirigir en el bloqueo. Si se establecen AXES_LOCKOUT_TEMPLATE y AXES_LOCKOUT_URL, se utilizara la plantilla.
AXES_LOCKOUT_TEMPLATE = '403.html' #Si esta configurado, especifica una plantilla para renderizar cuando un usuario esta bloqueado. La plantilla recibe cooloff_time y failure_limit como variables de contexto.
AXES_VERBOSE = True #Si es True , veras un poco mas de registro para los Ejes.

ROOT_URLCONF = 'sit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'sit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'UPSO',
        'USER': 'postgres',
        'PASSWORD': 'edplanificacion',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'es-bo'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]

MEDIA_URL = 'archivos/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/archivos')

STATIC_ROOT = 'staticos/'

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default':{
        'toolbar': None,
    },
}

IMAGENES_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/archivos')
#variable login
# LOGIN_URL = '/'
LOGIN_REDIRECT_URL = reverse_lazy('tramite:index')
LOGOUT_REDIRECT_URL = reverse_lazy('login')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True