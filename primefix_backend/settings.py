"""
Django settings for primefix_backend project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',  # Required by Django
    'corsheaders',
    'contact',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'primefix_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'primefix_backend.wsgi.application'


# Database - Not needed for this app, but Django requires it
# Using SQLite (file-based, zero configuration) - no form data is stored
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Note: We don't store form submissions - just send emails directly
# The database is only used by Django internally


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings - Allow all origins (set to True in production)
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

# If you want to restrict to specific origins, set CORS_ALLOW_ALL_ORIGINS=False and use this:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1",
]

# Email configuration for GoDaddy
# Using GoDaddy's own SMTP server (doesn't require SMTP AUTH to be enabled)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtpout.secureserver.net'  # GoDaddy's SMTP server
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'info@primefixusa.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'Primefixusa@11274')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'info@primefixusa.com')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'info@primefixusa.com')

# Microsoft Email Setup Instructions:
# 1. EMAIL_HOST_USER: Enter your full Microsoft email address (e.g., 'yourname@outlook.com')
# 2. EMAIL_HOST_PASSWORD: 
#    - If you DON'T have 2-factor authentication: Use your regular email password
#    - If you HAVE 2-factor authentication enabled: 
#      * Go to https://account.microsoft.com/security
#      * Click "Advanced security options"
#      * Under "App passwords", create a new app password
#      * Use that app password here
# 3. DEFAULT_FROM_EMAIL: Should match your EMAIL_HOST_USER (the email sending from)

