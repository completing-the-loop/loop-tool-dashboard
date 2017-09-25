from django.views.generic.base import TemplateView

from dashboard.models import CourseRepeatingEvent


class CourseContentView(TemplateView):
    template_name = 'dashboard/content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        repeating_events = CourseRepeatingEvent.objects.filter(course_offering=self.request.course_offering)

        context['no_weeks'] = self.request.course_offering.no_weeks
        context['repeating_events'] = repeating_events

        return context
