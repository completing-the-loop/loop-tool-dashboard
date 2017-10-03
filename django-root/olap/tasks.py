from django.conf import settings
from unipath.path import Path

from dashboard.models import CourseOffering
from django_site.celery import app
from olap.lms_import import ImportLmsData
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.models import SummaryPost
from olap.utils import get_course_export_data


@app.task(bind=True)
def import_olap_task(self, course_id, filename):
    course_offering = CourseOffering.objects.get(id=course_id)
    file_path = Path.join(settings.DATA_PROCESSING_DIR, filename)

    try:
        importer = ImportLmsData(course_offering, file_path)
        importer.process()

        latest_activity = [
            PageVisit.objects.filter(page__course_offering=course_offering).latest('visited_at').visited_at,
            SubmissionAttempt.objects.filter(page__course_offering=course_offering).latest('attempted_at').attempted_at,
            SummaryPost.objects.filter(course_offering=course_offering).latest('posted_at').posted_at,
        ]
        course_offering.last_activity_at = max(latest_activity)
    finally:
        course_offering.is_importing = False
        course_offering.save()


@app.task(bind=True)
def process_data_exports(self):
    processing_data_folder = settings.DATA_PROCESSING_DIR
    export_data = get_course_export_data()

    export_data_mapping = { course_offering['filename']: course_offering['id'] for course_offering in export_data['courses'].values() }

    import_files = Path(export_data['import_location']).listdir()

    for import_file in import_files:
        try:
            course_offering = CourseOffering.objects.get(id=export_data_mapping[import_file.name])
            import_file.move(processing_data_folder)
            course_offering.is_importing = True
            course_offering.save()

            import_olap_task.delay(course_offering.id, import_file.name)
        except KeyError:
            import_file.remove()

