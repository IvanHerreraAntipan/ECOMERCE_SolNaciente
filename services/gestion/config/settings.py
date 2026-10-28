"""
Django settings for config project (Servicio de Gestión).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# RNF-12: Sin secretos en texto plano
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key-for-dev')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nuestra app de usuarios y CMS
    'usuarios',
    # Librerías externas
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
]

# Le indicamos a Django que use nuestro modelo personalizado de Usuario:
AUTH_USER_MODEL = 'usuarios.Usuario'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Debe ir antes de CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# CC-05: Almacenamiento relacional en PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ecommerce_gestion'),
        'USER': os.getenv('DB_USER', 'ecommerce_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'ecommerce_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework & OpenAPI (RNF-05)
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'usuarios.authentication.SimpleTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Gestión - E-Commerce',
    'DESCRIPTION': 'Microservicio para identidad, usuarios, roles, CMS y contacto.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS (Permitir peticiones desde React Vite en el puerto 5173)
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') 
    if origin.strip()
]