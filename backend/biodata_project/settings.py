
# Standard library imports
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Logging configuration to capture errors and email issues (must come after BASE_DIR)
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Enhanced logging: log to both file and console for easier debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        # Log all app logs to console as well
        '': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
        },
    },
}

# Email configuration (use environment variables in production)
# For testing/development: use console backend to avoid sending real emails
# For production: use SMTP backend with proper credentials
EMAIL_BACKEND = os.environ.get(
    'DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'
)

# SMTP settings - MUST be set via environment variables
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'bhudevnetwork@gmail.com')

# ⚠️ SECURITY: Never hardcode passwords! Use environment variables
# For Gmail: You MUST use an App Password (not regular password)
# Generate App Password: https://myaccount.google.com/apppasswords
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'dnlu ghtb riut wkit')

# If password is not set, log a warning
if not EMAIL_HOST_PASSWORD and EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    import warnings
    warnings.warn(
        "EMAIL_HOST_PASSWORD is not set! Emails will fail to send. "
        "Set the EMAIL_HOST_PASSWORD environment variable or use console backend for testing.",
        RuntimeWarning
    )

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@yourdomain.com')
 
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'CHANGE_ME_TO_A_SECURE_RANDOM_KEY'
DEBUG = True
ALLOWED_HOSTS = [
    'keyla-mirier-pebbly.ngrok-free.dev',
    'www.keyla-mirier-pebbly.ngrok-free.dev',
    'localhost',
    '127.0.0.1'
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'biodata',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biodata_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Include the frontend root so Django can render the plain HTML files via TemplateView
        'DIRS': [
            BASE_DIR.parent,  # points to the project root that contains index.html, css/, js/, assets/
        ],
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

WSGI_APPLICATION = 'biodata_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# During development, serve the frontend's css/js/assets via Django staticfiles
# without changing the existing HTML paths.
STATICFILES_DIRS = [
    BASE_DIR.parent / 'css',
    BASE_DIR.parent / 'js',
    BASE_DIR.parent / 'assets',
]


# Allow CORS from the frontend during development and ngrok
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://keyla-mirier-pebbly.ngrok-free.dev',
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
