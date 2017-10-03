from django.core.management.base import BaseCommand

from olap.tasks import process_data_exports


class Command(BaseCommand):
    help = "Call the celery task to process the data exports."

    def handle(self, *args, **options):
        process_data_exports.delay()
