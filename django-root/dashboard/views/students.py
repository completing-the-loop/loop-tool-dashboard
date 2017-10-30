from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from dashboard.models import CourseRepeatingEvent
from olap.models import LMSUser


class StudentsView(TemplateView):
    template_name = 'dashboard/students.html'

    def get(self, request, *args, **kwargs):
        self.course_offering = request.course_offering

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        repeating_events = CourseRepeatingEvent.objects.filter(course_offering=self.course_offering)

        event = repeating_events.first()
        event_id = event.id if event else None

        initial_data = {
            'num_weeks': self.request.course_offering.no_weeks,
            'event_id': event_id,
            'course_id': self.request.course_offering.id,
        }

        context['initial_data'] = CamelCaseJSONRenderer().render(initial_data)
        context['repeating_events'] = repeating_events

        return context


# Placeholder class for detailed student view.  Will need modifying by whoever does this task.
class StudentDetailView(TemplateView):
    template_name = 'dashboard/student_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        student_id = kwargs.get('pk')
        student = get_object_or_404(LMSUser, pk=student_id, course_offering=self.request.course_offering)

        initial_data = {
            'course_id': self.request.course_offering.id,
            'course_start': self.request.course_offering.start_date,
            'num_weeks': self.request.course_offering.no_weeks,
            'student_id': student.id,
        }

        context['initial_data'] = CamelCaseJSONRenderer().render(initial_data)
        context['student'] = student

        return context
