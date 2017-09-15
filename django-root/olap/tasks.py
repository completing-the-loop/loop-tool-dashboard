from django.core.management import call_command

from django_site.celery import app


@app.task(bind=True)
def import_olap_task(self):
    call_command('import_olap_data')
