from django.views.generic.base import TemplateView
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from dashboard.models import CourseRepeatingEvent
from olap.models import Page


class CourseContentView(TemplateView):
    template_name = 'dashboard/content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        repeating_events = CourseRepeatingEvent.objects.filter(course_offering=self.request.course_offering)

        initial_data = {
            'num_weeks': self.request.course_offering.no_weeks,
            'event_id': repeating_events.first().id,
            'course_id': self.request.course_offering.id,
        }

        context['initial_data'] = CamelCaseJSONRenderer().render(initial_data)
        context['repeating_events'] = repeating_events

        return context


class CoursePageView(TemplateView):
    template_name = 'dashboard/course_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['course_page'] = Page.objects.get(pk=self.kwargs.get('pk'), course_offering=self.request.course_offering)

        return context
