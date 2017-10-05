from django.conf import settings

from dashboard.models import CourseOffering


def get_course_import_metadata():
    course_offerings = {}
    for course_offering in CourseOffering.objects.filter(is_importing=False):
        last_activity_at = course_offering.get_last_activity_date()

        course_offerings[course_offering.code] = {
            'id': course_offering.id,
            'course_code': course_offering.code,
            'last_activity': last_activity_at.isoformat(),
            'filename': '{}_{}.zip'.format(course_offering.code, int(last_activity_at.timestamp()))
        }

    api_data = {
        'import_location': settings.DATA_IMPORT_DIR,
        'courses': course_offerings
    }
    return api_data
