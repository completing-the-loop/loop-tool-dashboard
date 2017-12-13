"""
Staging settings and globals
"""
from distutils.util import strtobool as _strtobool
from unipath import Path as _Path

from .production_base import *

# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

ALLOWED_HOSTS = [
    # 'staging.mysite.com',
]

BODY_ENV_CLASS = 'env-staging'


# ----------------------------------------------------------------------------------------------------------------------
# Custom Project Configuration

DATA_IMPORT_DIR = _Path(get_env_setting('DATA_IMPORT_DIR'))
DATA_PROCESSING_DIR = _Path(get_env_setting('DATA_PROCESSING_DIR'))
DATA_ERROR_LOGS_DIR = _Path(get_env_setting('DATA_ERROR_LOGS_DIR'))


# ----------------------------------------------------------------------------------------------------------------------
if not _strtobool(get_env_setting('CI_SERVER', '0')):
    assert len(ADMINS) > 0
