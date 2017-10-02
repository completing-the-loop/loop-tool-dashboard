"""
Staging settings and globals
"""
from distutils.util import strtobool as _strtobool

from .production_base import *

# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

ALLOWED_HOSTS = [
    # 'staging.mysite.com',
]

BODY_ENV_CLASS = 'env-staging'

DATA_IMPORT_DIR = get_env_setting('DATA_IMPORT_DIR')

# ----------------------------------------------------------------------------------------------------------------------
if not _strtobool(get_env_setting('CI_SERVER', '0')):
    assert len(ADMINS) > 0
