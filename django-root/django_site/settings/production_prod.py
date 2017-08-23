"""
Production settings and globals
"""
from distutils.util import strtobool as _strtobool

from .production_base import *

# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

ALLOWED_HOSTS = [
    # 'www.mysite.com',
]

BODY_ENV_CLASS = 'env-prod'

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Only use HTTPS for various cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ----------------------------------------------------------------------------------------------------------------------
if not _strtobool(get_env_setting('CI_SERVER', '0')):
    assert len(ADMINS) > 0
