from django.conf import settings
from unipath.path import Path

from dashboard.models import CourseOffering
from django_site.celery import app
from olap.lms_import import ImportLmsData
from olap.utils import get_course_import_metadata


@app.task(bind=True)
def import_olap_task(self, course_id, filename, just_clear=False):
    course_offering = CourseOffering.objects.get(id=course_id)
    file_path = Path(settings.DATA_PROCESSING_DIR, filename)

    try:
        importer = ImportLmsData(course_offering, file_path, just_clear=just_clear)
        importer.process()
    finally:
        course_offering.is_importing = False
        course_offering.save()


@app.task(bind=True)
def preprocess_data_imports(self):
    processing_data_folder = settings.DATA_PROCESSING_DIR
    import_metadata = get_course_import_metadata()

    import_metadata_mapping = { course_offering['filename']: course_offering['id'] for course_offering in import_metadata['courses'].values() }

    import_files = Path(import_metadata['import_location']).listdir()

    for import_file in import_files:
        try:
            course_offering = CourseOffering.objects.get(id=import_metadata_mapping[import_file.name])
            import_file.move(processing_data_folder)
            course_offering.is_importing = True
            course_offering.save()

            import_olap_task.delay(course_offering.id, import_file.name)
        except KeyError:
            import_file.remove()

