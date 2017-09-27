from django.db import connections
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from dashboard.models import CourseOffering, CourseRepeatingEvent

class CourseCommunicationView(TemplateView):
    template_name = 'dashboard/communication.html'

    def get(self, request, *args, **kwargs):
        self.course_offering = request.course_offering

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course_weeks = self.course_offering.get_weeks()

        repeating_events = CourseRepeatingEvent.objects.filter(course_offering=self.course_offering)

        context['course_weeks'] = course_weeks
        context['course'] = self.course_offering
        context['repeating_events'] = repeating_events

        return context
