#!/usr/bin/env python
import os
import re
import sys

from unipath import Path

# On heroku don't worry about this check - the python buildpack runs
# collectstatic from the root directory
if not os.environ.get('HEROKU_ENV'):
    assert os.getcwd() == Path(__file__).absolute().parent, 'To avoid import path issues please run manage.py from within the django-root dir'


def find_file_recursive(filename):
    """Search for a file recursively up"""
    current_dir = Path(__file__).absolute().parent
    while current_dir and current_dir != current_dir.parent:
        fname = Path(current_dir, filename)
        if fname.isfile(): return fname
        current_dir = current_dir.parent
    return False


def read_env():
    """Pulled from Honcho (heroku) code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.
    """
    env_file = find_file_recursive('.env')
    if env_file:
        try:
            with open(env_file) as f:
                content = f.read()
                for line in content.splitlines():
                    m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
                    if m1:
                        key, val = m1.group(1), m1.group(2)
                        m2 = re.match(r"\A'(.*)'\Z", val)
                        if m2:
                            val = m2.group(1)
                        m3 = re.match(r'\A"(.*)"\Z', val)
                        if m3:
                            val = re.sub(r'\\(.)', r'\1', m3.group(1))
                        os.environ.setdefault(key, val)
        except (IOError, TypeError):
            pass


if __name__ == "__main__":
    read_env()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_site.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
