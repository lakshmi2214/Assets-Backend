
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Set these env vars for real email
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER if EMAIL_HOST_USER else 'webmaster@localhost'
