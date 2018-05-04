import os as _os
import sys as _sys
import platform as _platform

# FIXME: Replace with more generic development/production configuration

_dev_hosts = [
    ('MacBook-Pro', 'darwin'),
    ('MacBook-Pro.local', 'darwin'),
]


# can't just use use HOSTNAME as /usr/bin/env wipes it
_hostname = _platform.node()
if _os.environ.get('DJANGO_SETTINGS_MODULE') and _os.environ.get('DJANGO_SETTINGS_MODULE') != __name__:
    # Do nothing; handled by django importing a custom settings module directly
    pass
elif any(_hostname.endswith(dev_host) and _sys.platform == platform for (dev_host, platform) in _dev_hosts):
    from .dev import *  # noqa isort:skip
elif _hostname.endswith(_os.environ.get('DEV_MACHINE')):
    from .dev import *  # noqa isort:skip
else:
    # Normally you should not import ANYTHING from Django directly
    # into your settings, but ImproperlyConfigured is an exception.
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'Unrecognised host %s in %s. If this is a dev machine, add to _dev_hosts in %s' % (
            _hostname,
            __name__,
            _os.path.realpath(__file__)
        )
    )
