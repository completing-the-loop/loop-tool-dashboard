"""
Development settings and globals
"""
from distutils.util import strtobool as _strtobool
import hashlib as _hashlib
import random as _random
import re as _re
import sys as _sys
from unipath import Path as _Path

from .base import *

# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

DEBUG = True
DEBUG_WEBPACK = True
TESTING = get_env_setting('TESTING', False)

ALLOWED_HOSTS += [
    '127.0.0.1',
    'localhost',
]

# WSGI_APPLICATION = None

INTERNAL_IPS = [
    '127.0.0.1',
]

# Add this to your base template to alter styling based on the environment
# (eg change background colour depending on whether prod/stage/dev)
BODY_ENV_CLASS = 'env-dev'

# ----------------------------------------------------------------------------------------------------------------------
# Application definition

INSTALLED_APPS += (
    # 'ui_patterns',
)

# "DEBUG_TOOLBAR=0 ./manage.py runserver" to run server w/ django debug toolbar off.
if _strtobool(get_env_setting('DEBUG_TOOLBAR', '1')):
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'SKIP_TEMPLATE_PREFIXES': (
            'django/forms/widgets/',
            'admin/widgets/',
            'floppyforms/',     # needed to avoid infinite loops
        ),
    }


# ----------------------------------------------------------------------------------------------------------------------
# Template configuration

if DEBUG:
    for _tpl in TEMPLATES:
        _tpl['OPTIONS']['debug'] = True


# ----------------------------------------------------------------------------------------------------------------------
# Database Configuration
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES['default']['NAME'] = 'cloop'


# ----------------------------------------------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)

if DEBUG:
    WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = _Path(PROJECT_DIR, 'frontend/dist/webpack-stats-dev.json')

# ----------------------------------------------------------------------------------------------------------------------
# SECRET_KEY

# If there is no SECRET_KEY defined, will write one to disk so that sessions are preserved across restarts
SECRET_KEY = get_env_setting('SECRET_KEY', '')
if SECRET_KEY == '':
    import errno as _errno
    import subprocess as _subprocess

    try:
        with open(_Path(_Path(__file__).parent, 'SECRET_KEY'), 'r') as _fp:
            _unhashed_secret = _fp.read()
        if len(_unhashed_secret) == 0:
            # an empty file might as well not be there
            raise FileNotFoundError()
    except FileNotFoundError as e:
        with open(_Path(_Path(__file__).parent, 'SECRET_KEY'), 'wb') as _fp:
            _unhashed_secret = '\n'.join([
                '# This is an automatically generated secret key',
                '# DO NOT COMMIT THIS',
                '# DO NOT USE THIS FOR PRODUCTION',
                _hashlib.sha256(str(_random.SystemRandom().getrandbits(256)).encode('utf-8')).hexdigest(),
            ])
            _fp.write(_unhashed_secret.encode('utf-8'))
    # This slows down startup by 0.3-0.4 sec, but ensures that we have a semi-randomised output that will fail
    # on linux, so should make it harder to predict the SECRET_KEY if it is accidentally committed to source
    _proc = _subprocess.Popen(['system_profiler', 'SPStorageDataType'], stdout=_subprocess.PIPE)
    _unhashed_secret += '\n' + '\n'.join(sorted(str(line) for line in _proc.communicate()[0].splitlines() if b'UUID' in line))
    SECRET_KEY = _hashlib.sha256(_unhashed_secret.encode('utf-8')).hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
# Logging
if DEBUG:
    LOGGING['loggers']['werkzeug']['level'] = 'DEBUG'
    # LOGGING['loggers']['django.db.backends']['handlers'].append('console')    # uncomment to see SQL queries
    LOGGING['loggers']['django']['handlers'].append('console')


# ----------------------------------------------------------------------------------------------------------------------
# Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ----------------------------------------------------------------------------------------------------------------------
# Note that manage.py runserver forks processes so this will unavoidably display multiple times
_dev_notice_printed = False
if not _dev_notice_printed:
    # Only prints dev config if no arguments (makes bash tab-complete cleaner)
    if _re.search(r'(^|/)(manage\.py|django-admin(\.py)?)$', _sys.argv[0]) and len(_sys.argv) != 1:
        import os as _os
        print("Loaded dev config (pid %d)\n" % _os.getpid(), file=_sys.stderr)
        _dev_notice_printed = True
