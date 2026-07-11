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

# ALLOWED_HOSTS - Django doesn't support wildcards like *.onrender.com
# So we'll use * to allow all hosts (for Render deployment)
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '*')
if '*' in allowed_hosts_str or 'onrender.com' in allowed_hosts_str:
    # Accept all hosts for Render deployment
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',  # Required by Django
    'corsheaders',
    'contact',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS must be first
    'django.middleware.security.SecurityMiddleware',
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

# Email configuration - provider-agnostic SMTP via environment variables
EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER', '').strip().lower()
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.office365.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', EMAIL_HOST_USER)
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '8'))
MS_GRAPH_TENANT_ID = os.environ.get('MS_GRAPH_TENANT_ID', '')
MS_GRAPH_CLIENT_ID = os.environ.get('MS_GRAPH_CLIENT_ID', '')
MS_GRAPH_CLIENT_SECRET = os.environ.get('MS_GRAPH_CLIENT_SECRET', '')
MS_GRAPH_SENDER_USER = os.environ.get('MS_GRAPH_SENDER_USER', EMAIL_HOST_USER)
SMTP_DIAG_TOKEN = os.environ.get('SMTP_DIAG_TOKEN', '')
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', DEFAULT_FROM_EMAIL)
BREVO_SENDER_NAME = os.environ.get('BREVO_SENDER_NAME', 'Primefix')

USE_MICROSOFT_GRAPH = all([
    MS_GRAPH_TENANT_ID,
    MS_GRAPH_CLIENT_ID,
    MS_GRAPH_CLIENT_SECRET,
    MS_GRAPH_SENDER_USER,
    RECIPIENT_EMAIL,
])

USE_BREVO = bool(BREVO_API_KEY and BREVO_SENDER_EMAIL and RECIPIENT_EMAIL)

if not EMAIL_PROVIDER:
    if USE_BREVO:
        EMAIL_PROVIDER = 'brevo'
    elif USE_MICROSOFT_GRAPH:
        EMAIL_PROVIDER = 'graph'
    else:
        EMAIL_PROVIDER = 'smtp'

# Example SMTP env vars for a non-Office365 provider:
# EMAIL_HOST=smtp.provider.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_USE_SSL=False
# EMAIL_HOST_USER=your-smtp-username
# EMAIL_HOST_PASSWORD=your-smtp-password
# DEFAULT_FROM_EMAIL=your-sender@domain.com
# RECIPIENT_EMAIL=your-inbox@domain.com
# For Microsoft Graph instead of SMTP, set:
# MS_GRAPH_TENANT_ID=your-azure-tenant-id
# MS_GRAPH_CLIENT_ID=your-app-client-id
# MS_GRAPH_CLIENT_SECRET=your-app-client-secret
# MS_GRAPH_SENDER_USER=info@yourdomain.com
# For Brevo API instead of SMTP, set:
# EMAIL_PROVIDER=brevo
# BREVO_API_KEY=your-brevo-api-key
# BREVO_SENDER_EMAIL=info@yourdomain.com
# BREVO_SENDER_NAME=Primefix

