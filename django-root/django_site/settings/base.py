"""
Django settings common to all environments

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/topics/settings/
"""
import os as _os
import sys as _sys

from unipath import Path as _Path


def get_env_setting(setting, default=None):
    """ Get the environment setting or return exception """
    x = _os.environ.get(setting, default)
    if x is not None:
        return x
    else:
        error_msg = "Environment variable %s is not set" % setting
        import django.core.exceptions
        raise django.core.exceptions.ImproperlyConfigured(error_msg)


# ----------------------------------------------------------------------------------------------------------------------
# Core Site configuration

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Use debug webpack server? (if not, will assume prod webpack build)
DEBUG_WEBPACK = False

# Allowed hosts when DEBUG is on
ALLOWED_HOSTS = []

# wsgi application (only applies to django runserver)
WSGI_APPLICATION = 'wsgi.application'

# Add this to your base template to alter styling based on the environment
# (eg change background colour depending on whether prod/stage/dev)
BODY_ENV_CLASS = 'env-unknown'


# ----------------------------------------------------------------------------------------------------------------------
# Basic path configuration

# Absolute filesystem path to the Django project root directory (the directory that contains the site module)
BASE_DIR = _Path(__file__).ancestor(3)

# Absolute filesystem path to the top-level project folder (usually the root of the git repo)
PROJECT_DIR = BASE_DIR.parent

# Site name
SITE_NAME = BASE_DIR.name

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
_sys.path.insert(0, BASE_DIR)


# ----------------------------------------------------------------------------------------------------------------------
# Manager configuration
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
# These people will get error emails
ADMINS = (
    #('Receipient', 'address@alliancesoftware.com.au'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
# Will get broken link notifications if BrokenLinkEmailsMiddleware is enabled
MANAGERS = ADMINS


# ----------------------------------------------------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = (
    # order matters!
    # static files/templates/commands all go to the first app listed that matches
    # however model dependencies need to be constructed in order

    # project specific
    'django_site',
    'dashboard',
    'olap',

    # 3rd party
    # 'admin_steroids',
    'allianceutils',
    'authtools',
    # 'ckeditor',
    # 'ckeditor_uploader',
    # 'compat',
    # 'compressor',
    # 'django_admin_bootstrapped',    # Must come before django.contrib.admin
    'django_extensions',
    # 'django_select2',
    # 'django_tables2',
    # 'filebrowser',
    # 'floppyforms',
    # 'form_utils',
    'hijack',
    # 'import_export',
    'rest_framework',
    'rules.apps.AutodiscoverRulesConfig',
    # 'webpack_loader',

    # core django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

# Order matters!
# See https://docs.djangoproject.com/en/1.8/ref/middleware/#middleware-ordering
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',    # various security, ssl settings (django >=1.9)
    # 'django.middleware.gzip.GZipMiddleware',            # compress responses. Consider @gzip_page() instead
    # 'django.middleware.http.ConditionalGetMiddleware',  # conditional etag caching
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.common.BrokenLinkEmailsMiddleware',
    # 'allianceutils.middleware.CurrentUserMiddleware',

    # 'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware', # fall back to static html on 404
    # 'django.contrib.redirects.middleware.RedirectFallbackMiddleware', # fall back to redirect on 404
)

# ----------------------------------------------------------------------------------------------------------------------
# URL configuration

# Append missing / to requests and redirect?
APPEND_SLASH = False
# Prepend missing www. to requests and redirect?
PREPEND_WWW = False

# Site root urls
ROOT_URLCONF = 'django_site.urls'


# ----------------------------------------------------------------------------------------------------------------------
# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # global template dirs
        ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',

                # project-specific custom global context processors
            ],
            'debug': DEBUG,
            # Only one of APP_DIRS and loaders should be set
            'loaders': [
                # 'apptemplates.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]


# ----------------------------------------------------------------------------------------------------------------------
# Database Configuration
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        # mysql
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET default_storage_engine=INNODB; SET sql_mode='STRICT_TRANS_TABLES'",
            'read_default_file': '~/.my.cnf',
            'charset': 'utf8mb4',
        },
    }
}

# ----------------------------------------------------------------------------------------------------------------------
# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-au'

TIME_ZONE = 'Australia/Melbourne'

USE_TZ = True

# Enable translations?
USE_I18N = False

# Enable locale-aware date/time/currency/number formatting
USE_L10N = False

# only applies if USE_L10N is on (and humanize template tags are used)
# USE_THOUSAND_SEPARATOR = True


# ----------------------------------------------------------------------------------------------------------------------
# Date formats

# Application-specific date formats
# If USE_L10N is on you may want to consider using django.util.formats.date_format(..)
# For adding custom formats: https://docs.djangoproject.com/en/dev/topics/i18n/formatting/#creating-custom-format-files

# http://strftime.org/
FORMAT_DATE = '%-d %b %Y'               # 5 Oct 2017
FORMAT_DATE_SHORT = '%-d/%m/%Y'         # 5/10/2006

FORMAT_DATE_WEEKDAY = "%a %-d %b %Y"    # Thu 5 Oct 2017
FORMAT_DATE_YEAR_MONTH = '%b %Y'        # Oct 2017
FORMAT_DATE_MONTH_DAY = '%-d %b'        # 5 Oct

FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'               # 2017-10-05 01:23:45
FORMAT_DATETIME_SHORT = '%-d/%m/%Y %-I:%M:%S %p'    # 5/10/2006 1:23:45 am

FORMAT_DATE_ISO = '%Y-%m-%d'                # 2017-10-05
FORMAT_DATETIME_ISO = '%Y-%m-%d %H:%M:%S'   # 2017-10-05 01:23:45

FORMAT_DATE_COMPACT = '%Y%m%d'              # 20171005
FORMAT_DATETIME_COMPACT = '%Y%m%.d%H%M%S'   # 20171005.012345

if not USE_L10N:
    # Django date formats (used in templates only)
    # These only apply if USE_L10N is off
    def _convert_date_format(fmt):
        # convert from python format string to django format string
        mapping = {
            '%a': 'D',
            '%A': 'l',
            '%b': 'M',
            '%B': 'F',
            '%c': '',
            '%d': 'd',
            '%-d':'j',
            '%f': '',
            '%H': 'H',
            '%-H':'G',
            '%I': 'h',
            '%-I':'g',
            '%j': 'z',
            '%m': 'm',
            '%-m':'n',
            '%M': 'i',
            '%p': 'A',
            '%S': 's',
            '%U': '',
            '%w': 'w',
            '%W': 'W',
            '%x': '',
            '%X': '',
            '%y': 'y',
            '%Y': 'Y',
            '%z': 'O',
            '%Z': 'e',
        }
        for py, php in mapping.items():
            fmt = fmt.replace(py, php)
        return fmt

    # See https://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-date for format
    DATE_FORMAT = _convert_date_format(FORMAT_DATE)
    DATETIME_FORMAT = _convert_date_format(FORMAT_DATETIME)
    YEAR_MONTH_FORMAT = _convert_date_format(FORMAT_DATE_YEAR_MONTH)
    MONTH_DAY_FORMAT = _convert_date_format(FORMAT_DATE_MONTH_DAY)
    SHORT_DATE_FORMAT = _convert_date_format(FORMAT_DATE_SHORT)
    SHORT_DATETIME_FORMAT = _convert_date_format(FORMAT_DATETIME_SHORT)


# ----------------------------------------------------------------------------------------------------------------------
# Upload dirs

# local file storage
MEDIA_URL = '/media/'
# os.path.join() starts at the latest absolute path - so remove leading slash
# from MEDIA_URL before joining
MEDIA_ROOT = _Path(PROJECT_DIR, MEDIA_URL.strip(_os.sep))

# Use S3 for file storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
# TODO: allianceutils.storage.MediaStorage is wrapper to django-storages; need test cases for this
# DEFAULT_FILE_STORAGE = 'allianceutils.storage.MediaStorage'
# This is used as a prefix for media files in the S3 bucket
# MEDIAFILES_LOCATION = 'media'
# AWS_HEADERS = {'Cache-Control': 'max-age=86400'}
# AWS_STORAGE_BUCKET_NAME = get_env_setting('AWS_BUCKET')
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)

# ----------------------------------------------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = PROJECT_DIR.child('assets').norm()

STATIC_URL = '/static/'

# non-app static file locations
STATICFILES_DIRS = (
    ('dist/prod', _Path(PROJECT_DIR, 'frontend/dist/production')),
    #_Path(PROJECT_DIR, 'node_modules/bootstrap-sass/assets/stylesheets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Uncomment this to store static files on S3.
# Note that this causes problems with heroku pipelines as the promotion doesn't take care of static files.
# STATICFILES_STORAGE = 'allianceutils.storage.StaticStorage'
# This is used as a prefix for static files in the S3 bucket
# STATICFILES_LOCATION = 'static'


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/prod/',
        'STATS_FILE': _Path(PROJECT_DIR, 'frontend/dist/prod/webpack-stats.json'),
        'LOADER_CLASS': 'allianceutils.webpack.TimestampWebpackLoader',
    },
}


# ----------------------------------------------------------------------------------------------------------------------
# SECRET_KEY

# (entirely in dev/prod)

# ----------------------------------------------------------------------------------------------------------------------
# AWS keys
# Usually used with django-storages
# AWS_SECRET_ACCESS_KEY = get_env_setting('AWS_SECRET_ACCESS_KEY')
# AWS_ACCESS_KEY_ID = get_env_setting('AWS_ACCESS_KEY')

# ----------------------------------------------------------------------------------------------------------------------
# User auth/permissions configuration

AUTH_USER_MODEL = 'authtools.User'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/admin/login/?next=/admin/'
LOGIN_REDIRECT_URL = '/admin/'

# Hijack
HIJACK_ALLOW_GET_REQUESTS = False
HIJACK_AUTHORIZE_STAFF = False
HIJACK_USE_BOOTSTRAP = True


# ----------------------------------------------------------------------------------------------------------------------
# Logging

LOG_DIR = _Path(PROJECT_DIR, 'log')
assert LOG_DIR.exists()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': FORMAT_DATETIME,
        },
        'simple_request': {
            'format': '[%(asctime)s] %(levelname)s %(status_code)s %(message)s',
            'datefmt': FORMAT_DATETIME,
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(module)s %(process)d %(thread)d [%(name)s:%(lineno)s] %(message)s',
            'datefmt': FORMAT_DATETIME,
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },

    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _Path(LOG_DIR, 'debug.log'),
            'maxBytes': 10 * 1000 * 1000,
            'backupCount': 1,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _Path(LOG_DIR, 'error.log'),
            'maxBytes': 10 * 1000 * 1000,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'file_request': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _Path(LOG_DIR, 'request.log'),
            'maxBytes': 100 * 1000 * 1000,
            'backupCount': 4,
            'formatter': 'simple_request',
        },

        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },

    'loggers': {
        # debugging logs
        'debug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },

        # django catch-all
        'django': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False,
        },

        # web requests (5xx=error, 4xx=warning, 3xx/2xx=info)
        'django.request': {
            'handlers': ['file_request'],
            'level': 'INFO',
            'propagate': False,
        },

        # database queries (
        'django.db.backends': {
            'handlers': [],
            'filter': ['require_debug_true'],
            'level': 'DEBUG',
            'propagate': False,
        },

        # todo: what is this used for?
        'net': {
            'handlers': [
                'mail_admins',
                'file_request',
            ],
            'level': 'INFO',
            'propagate': True,
        },
        # Sometimes monitoring triggers this and you will want to disable it
        # (although really you should configure the web server to deal with such requests)
        # 'django.security.DisallowedHost': {
        #     'handlers': ['file_request'],
        #     'propagate': False,
        # },

        # Note that prior to 1.10, django runserver is hardcoded to always mix everything into stderr so you have
        # to use runserver_plus/werkzeug to control output for CI
        # runserver/runserver_plus requests
        'django.server': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'werkzeug': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# ----------------------------------------------------------------------------------------------------------------------
# Email

# (entirely configured in prod/dev)


# ----------------------------------------------------------------------------------------------------------------------
# Serialization

SERIALIZATION_MODULES = {
     'json': 'allianceutils.serializers.json_orminheritancefix',
     'json_ordered': 'allianceutils.serializers.json_ordered',
}


# ----------------------------------------------------------------------------------------------------------------------
# APIs
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # we prioritise BasicAuthentication so that we can distinguish logged out (401) vs permission denied (403)
        # http response codes; our code doesn't actually use http basic authentication
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # default to requiring authentication & a role
        # you can override this by setting the permission_classes to AllowAny in the view
        'rest_framework.permissions.IsAuthenticated',
        'allianceutils.api.permissions.SimpleDjangoObjectPermissions',
    ),
}


# ----------------------------------------------------------------------------------------------------------------------
# Form Rendering
# DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

# django-filter
# Disable all help text unless explicitly include
# FILTERS_HELP_TEXT_EXCLUDE = False
# FILTERS_HELP_TEXT_FILTER = False


# ----------------------------------------------------------------------------------------------------------------------
# CKEditor
# CKEDITOR_IMAGE_BACKEND = 'pillow'
# CKEDITOR_UPLOAD_PATH = 'ckeditor/uploads/'
# CKEDITOR_BROWSE_SHOW_DIRS = True
# CKEDITOR_ALLOW_NONIMAGE_FILES = False
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': [
#             ["Format", "Bold", "Italic", "Underline", "Strike", "SpellChecker"],
#             ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter', 'JustifyRight',
#              'JustifyBlock'],
#             ["Image", "Table", "Link", "Unlink", "Anchor", "SectionLink", "Subscript", "Superscript"],
#             ['Undo', 'Redo'], ["Source"],
#             ["Maximize"]
#         ],
#     },
# }

# ----------------------------------------------------------------------------------------------------------------------
# django-permanent field
# PERMANENT_FIELD = 'deleted_at'


# ----------------------------------------------------------------------------------------------------------------------
# Frontend Testing Settings

# "MOCK_DATE_START="2017-01-01T10:00:00Z" ./manage.py runserver" to run server with system clock mocked out for testing
_start_time = get_env_setting('MOCK_DATE_START', '')
if _start_time:
    import freezegun as _freezegun
    _freezegun.freeze_time(_start_time, tick=True).start()
    print("Mocked out system clock to start at %s\n" % _start_time, file=_sys.stderr)

