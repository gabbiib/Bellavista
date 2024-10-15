"""
Django settings for app_bellavista project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9e-89o7ml=cfodeampd#kh1*3fhc&8xjsnqa$g%e7qmrkd65vp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion_usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app_bellavista.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'app_bellavista.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'BD_trabajadores',
        'USER': 'postgres',
        'PASSWORD': 'Gabriel_oli66',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

# settings.py
LOGOUT_REDIRECT_URL = '/login/'  


import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Usa sesiones basadas en base de datos

LOGIN_URL = '/accounts/login/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


SESSION_COOKIE_SECURE = False  # Cambia a True si estás en producción con HTTPS
CSRF_COOKIE_SECURE = False    # Cambia a True si estás en producción con HTTPS

AUTH_USER_MODEL = 'appcanal.Usuarios'


SESSION_COOKIE_AGE = 1209600  # Duración en segundos (2 semanas)

#import os
#from dotenv import load_dotenv  # Importa la función para cargar .env

# Cargar las variables del archivo .env
#load_dotenv()

# Ahora puedes acceder a las variables con os.getenv
#SECRET_KEY = os.getenv('SECRET_KEY')
#EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
#EMAIL_HOST = os.getenv('EMAIL_HOST')
#EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))  # Pasa a entero si es necesario
#EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
#EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL') == 'True'
#EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
#EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
#DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
#ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

#TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
#TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
#TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

