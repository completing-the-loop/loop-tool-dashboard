"""
WSGI config for gettingstarted project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

# This must come before whitenoise import below as it relies on it being set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_site.settings")

from django.core.wsgi import get_wsgi_application	# noqa isort:skip
from whitenoise.django import DjangoWhiteNoise		# noqa isort:skip

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
