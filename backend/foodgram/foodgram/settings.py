import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', default='default')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'djoser',
    'rest_framework',
    'users',
    'django_filters',
    'recipes',
    'api',
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

ROOT_URLCONF = 'foodgram.urls'

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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'django'),
        'USER': os.getenv('POSTGRES_USER', 'django_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'foodgram-db-1'),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}
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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserCreationSerializer',
    },
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['api.permissions.IsAdminOrReadOnly'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user_delete': ['rest_framework.permissions.IsAdminUser'],
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# ======= Константы для моделей =======
EMAIL_MAX_LENGHT = 254
USERNAME_MAX_LENGHT = 150
FIRST_USERNAME_MAX_LENGHT = 150
LAST_USERNAME_MAX_LENGHT = 150
PASSWORD_MAX_LENGHT = 150
INGREDIENT_MIN_AMOUNT = 1
RECIPE_NAME = 200
RECIPE_TEXT = 500
INGREDIENT_NAME = 150
INGREDIENT_UNIT = 20
TAG_NAME = 80
TAG_SLUG = 100
TAG_COLOR = 7

FILE_NAME = 'shopping_cart.txt' # Имя файла-списка покупок