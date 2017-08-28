from django.views.generic.base import TemplateView

from dashboard.models import Course


class CourseListView(TemplateView):
    template_name = 'dashboard/course_list.html'

    def get_context_data(self, **kwargs):
        courses = Course.objects.filter(owner=self.request.user)

        context = super().get_context_data(**kwargs)
        context['courses'] = courses
        return context