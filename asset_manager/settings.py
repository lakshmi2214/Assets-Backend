import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Try loading .env.local first, then .env
env_local_path = BASE_DIR / '.env.local'
if env_local_path.exists():
    load_dotenv(env_local_path)
else:
    load_dotenv()

SECRET_KEY = 'django-insecure-placeholder-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'assets',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'assets.middleware.PersistAdminSessionMiddleware',  # Keeps admin session alive on Vercel
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asset_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'asset_manager.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

import dj_database_url
# Check for DATABASE_URL (Vercel Postgres or other external DB)
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
# Fallback to SQLite (in /tmp) if no external DB is configured
elif 'VERCEL' in os.environ:
    import shutil
    DB_FILE = 'db.sqlite3'
    # Copy the database to /tmp so it is writable
    # Note: /tmp is ephemeral, data will reset on new deployments/cold starts
    tmp_db = os.path.join('/tmp', DB_FILE)
    if not os.path.exists(tmp_db):
        src_db = BASE_DIR / DB_FILE
        if os.path.exists(src_db):
            shutil.copy2(src_db, tmp_db)
    
    DATABASES['default']['NAME'] = tmp_db

    # Fix for Media files (uploads) on Vercel
    # Redirect MEDIA_ROOT to /tmp/media because default location is read-only
    MEDIA_ROOT = os.path.join('/tmp', 'media')
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
    src_media_dir = BASE_DIR / 'media'
    if os.path.exists(src_media_dir):
        shutil.copytree(src_media_dir, MEDIA_ROOT, dirs_exist_ok=True)

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Media (user uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Fix for Vercel: Use writable /tmp directory for media
if 'VERCEL' in os.environ:
    import shutil
    MEDIA_ROOT = os.path.join('/tmp', 'media')
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
    src_media_dir = BASE_DIR / 'media'
    if os.path.exists(src_media_dir):
        shutil.copytree(src_media_dir, MEDIA_ROOT, dirs_exist_ok=True)

# Cloudinary Integration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dx6tl6aa2'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '848777134372957'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', '4Ats9tHCHQeL0Nl55_vL76Qe2N4'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'https://asset-booking-frontendn.vercel.app',
    'https://asset-booking-backend.vercel.app',
    'https://assets-backend-ochre.vercel.app',
    'https://lakshmi2214.github.io',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http://localhost(:\d+)?$',
    r'^http://127\.0\.0\.1(:\d+)?$',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'https://asset-booking-frontendn.vercel.app',
    'https://asset-booking-backend.vercel.app',
    'https://assets-backend-ochre.vercel.app',
    'https://lakshmi2214.github.io',
]

# Session and Security Configuration
# On Vercel (Serverless), use signed cookies so session survives across cold starts.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# Vercel sits behind a proxy, we must tell Django to trust the HTTPS header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security settings for cookies
if os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
else:
    # Local development settings
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS', '')

