from functools import wraps

from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from dashboard.models import CourseOffering


# This wrapper applies course ownership rules to the wrapped URLs
def course_access_url_wrapper(view_func):
    @wraps(view_func)
    def course_access_func(request, course_id, *args, **kwargs):
        request.course_offering = get_object_or_404(CourseOffering, pk=course_id)
        if request.user.has_perm('dashboard.is_course_offering_owner', request.course_offering):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('You do not have access to that course')

    return course_access_func
