from django.core.management.base import BaseCommand

from olap.lms_import import ImportLmsData

class Command(BaseCommand):
    help = "Import OLAP data"

    def handle(self, *args, **options):
        importer = ImportLmsData()
        importer.process()
