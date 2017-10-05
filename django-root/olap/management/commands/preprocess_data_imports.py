from django.core.management.base import BaseCommand

from olap.tasks import preprocess_data_imports


class Command(BaseCommand):
    help = "Call the celery task to pre-process the OLAP data imports."

    def handle(self, *args, **options):
        preprocess_data_imports.delay()
