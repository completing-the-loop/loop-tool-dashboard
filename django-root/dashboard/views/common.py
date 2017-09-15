from dashboard.models import CourseOffering


class CourseMixin(object):

    def dispatch(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        self.course = CourseOffering.objects.get(pk=course_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context
