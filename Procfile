# Heroku process configuration
web: cd django-root && waitress-serve --port=$PORT django_site.wsgi:application
release: cd django-root && ./manage.py migrate --noinput
