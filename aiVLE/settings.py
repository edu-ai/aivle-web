"""
Django settings for aiVLE project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['cs4246.comp.nus.edu.sg', 'cs4246-i.comp.nus.edu.sg', '127.0.0.1', 'localhost', '*']
CORS_ALLOW_ALL_ORIGINS = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    "bootstrap4",
    'bootstrap_datepicker_plus',
    'fontawesome_5',
    'rest_framework',
    'rest_framework.authtoken',
    'prettyjson',
    'updateable',
    'app',
    'scheduler',
    'channels',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'corsheaders',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'updateable.middleware.UpdateableMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'aiVLE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.announcements',
            ],
        },
    },
]

WSGI_APPLICATION = 'aiVLE.wsgi.application'
# Channels
ASGI_APPLICATION = 'aiVLE.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Reference:

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Auth

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Messages

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Crispy form

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Permissions

ROLES_COURSE_ADD = ['LEC', 'ADM']
ROLES_COURSE_DELETE = ['LEC', 'ADM']
ROLES_COURSE_VIEW = ['GUE', 'STU', 'TA', 'LEC', 'ADM']
ROLES_COURSE_JOIN = ['GUE', 'STU', 'TA', 'LEC', 'ADM']
ROLES_TASK_VIEW = ['GUE', 'STU', 'TA', 'LEC', 'ADM']
ROLES_TASK_VIEW_ALL = ['TA', 'LEC', 'ADM']  # view unpublished tasks
ROLES_TASK_SUBMIT = ['STU', 'TA', 'LEC', 'ADM']
ROLES_TASK_ADD = ['LEC', 'ADM']
ROLES_TASK_EDIT = ['TA', 'LEC', 'ADM']
ROLES_TASK_DELETE = ['LEC', 'ADM']
ROLES_TASK_DOWNLOAD = ['LEC', 'ADM', 'TA']
ROLES_SUBMISSION_DOWNLOAD = ['LEC', 'ADM', 'TA']
ROLES_SUBMISSION_VIEW = ['LEC', 'ADM', 'TA']
ROLES_SUBMISSION_RERUN = ['LEC', 'ADM', 'TA']

ROLES = {
    'course.view': ROLES_COURSE_VIEW,
    'course.add': ROLES_COURSE_ADD,
    'course.delete': ROLES_COURSE_DELETE,
    'course.join': ROLES_COURSE_JOIN,
    'task.view': ROLES_TASK_VIEW,
    'task.add': ROLES_TASK_ADD,
    'task.edit': ROLES_TASK_EDIT,
    'task.delete': ROLES_TASK_DELETE,
    'task.submit': ROLES_TASK_SUBMIT,
    'task.download': ROLES_TASK_DOWNLOAD,
    'submission.download': ROLES_SUBMISSION_DOWNLOAD,
    'submission.view': ROLES_SUBMISSION_VIEW,
    'submission.rerun': ROLES_SUBMISSION_RERUN,
}

# Upload

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

# Django Rest Framework

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# DRF authentication

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'

# URL prefix to make SoC reverse proxy happy
# DOMAIN_NAME_PREFIX = r'projects/aivle/'
DOMAIN_NAME_PREFIX = None
