from django.conf import settings

from dashboard.models import CourseOffering


def get_course_import_metadata(lms_server=None):
    course_offerings_output = {}

    course_offerings = CourseOffering.objects.filter(is_importing=False)
    if lms_server:
        course_offerings = course_offerings.filter(lms_server=lms_server)
        server_name = lms_server.name
    else:
        server_name = ''

    for course_offering in course_offerings:

        if course_offering.lms_server:
            # Only show those attached to an LMS server
            last_activity_at = course_offering.get_last_activity_date()

            course_offerings_output[course_offering.code] = {
                'id': course_offering.id,
                'course_code': course_offering.code,
                'last_activity': last_activity_at.isoformat(),
                'course_end': course_offering.end_datetime.isoformat(),
                'filename': '{}_{}_{}.zip'.format(course_offering.lms_server.id, course_offering.code, int(last_activity_at.timestamp()))
            }

    api_data = {
        'server': server_name,
        'import_location': settings.DATA_IMPORT_DIR,
        'courses': course_offerings_output
    }
    return api_data
