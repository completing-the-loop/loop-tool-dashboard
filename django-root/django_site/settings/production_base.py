"""
Common settings for production/staging/ci etc
"""
from .base import *

# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

ALLOWED_HOSTS = [
    # overridden in the hostname_*.py files
]


# ----------------------------------------------------------------------------------------------------------------------
# SECRET_KEY
SECRET_KEY = get_env_setting('SECRET_KEY')


# ----------------------------------------------------------------------------------------------------------------------
# Database Configuration
DATABASES['default']['HOST'] = get_env_setting('DB_HOST')
DATABASES['default']['NAME'] = get_env_setting('DB_NAME')
DATABASES['default']['USER'] = get_env_setting('DB_USER')
DATABASES['default']['PASSWORD'] = get_env_setting('DB_PASSWORD')


# ----------------------------------------------------------------------------------------------------------------------
# Email Configuration

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_setting('EMAIL_HOST', 'localhost')
EMAIL_PORT = get_env_setting('EMAIL_PORT', 25)
EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
# EMAIL_TIMEOUT =
# EMAIL_FILE_PATH =


# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
SITE_NAME = 'cloop'
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = 'webmaster@localhost'


# ----------------------------------------------------------------------------------------------------------------------
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# ----------------------------------------------------------------------------------------------------------------------
# Logging configuration
LOGGING['loggers']['django']['handlers'].append('mail_admins')
LOGGING['loggers']['django.request']['handlers'].append('mail_admins')


# ----------------------------------------------------------------------------------------------------------------------
# Celery and RabbitMQ

RABBITMQ_USER = get_env_setting('RABBITMQ_USER')
RABBITMQ_PASSWORD = get_env_setting('RABBITMQ_PASSWORD')
RABBITMQ_HOSTNAME = get_env_setting('RABBITMQ_HOSTNAME')
RABBITMQ_PORT = get_env_setting('RABBITMQ_PORT')
RABBITMQ_VHOST = get_env_setting('RABBITMQ_VHOST')

CELERY_BROKER_URL = 'amqp://{}:{}@{}:{}/{}'.format(RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_VHOST)

CLOOP_IMPORT_ADMINS = get_env_setting('CLOOP_IMPORT_ADMINS').split(',')
