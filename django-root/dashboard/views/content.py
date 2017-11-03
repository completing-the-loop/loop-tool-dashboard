from django.shortcuts import get_object_or_404
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


class ResourcePageView(TemplateView):
    template_name = 'dashboard/resource_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resource_id = kwargs.get('pk')
        page = get_object_or_404(Page, pk=resource_id, course_offering=self.request.course_offering)

        initial_data = {
            'course_id': self.request.course_offering.id,
            'course_start': self.request.course_offering.start_date,
            'num_weeks': self.request.course_offering.no_weeks,
            'resource_id': page.id,
        }
        context['initial_data'] = CamelCaseJSONRenderer().render(initial_data)

        context['resource_page'] = page

        return context
