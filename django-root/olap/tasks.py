from django.conf import settings
from unipath.path import Path

from dashboard.models import CourseOffering
from django_site.celery import app
from olap.lms_import import ImportLmsData
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.models import SummaryPost
from olap.utils import get_course_import_metadata


@app.task(bind=True)
def import_olap_task(self, course_id, filename, just_clear=False):
    course_offering = CourseOffering.objects.get(id=course_id, just_clear=just_clear)
    file_path = Path.join(settings.DATA_PROCESSING_DIR, filename)

    try:
        importer = ImportLmsData(course_offering, file_path)
        importer.process()

        latest_activity = []

        try:
            latest_activity.append(PageVisit.objects.filter(page__course_offering=course_offering).latest('visited_at').visited_at)
        except PageVisit.DoesNotExist:
            pass

        try:
            latest_activity.append(SubmissionAttempt.objects.filter(page__course_offering=course_offering).latest('attempted_at').attempted_at)
        except SubmissionAttempt.DoesNotExist:
            pass

        try:
            latest_activity.append(SummaryPost.objects.filter(course_offering=course_offering).latest('posted_at').posted_at)
        except SummaryPost.DoesNotExist:
            pass

        if len(latest_activity):
            course_offering.last_activity_at = max(latest_activity)
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

