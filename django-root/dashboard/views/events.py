from django.urls.base import reverse
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from dashboard.forms import CourseRepeatingEventForm
from dashboard.forms import CourseSubmissionEventForm
from dashboard.models import CourseRepeatingEvent
from dashboard.models import CourseSubmissionEvent
from dashboard.views.common import CourseMixin


class CourseRepeatingEventListView(CourseMixin, ListView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_events_list.html'
    paginate_by = 10


class CourseRepeatingEventCreateView(CourseMixin, CreateView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_event_form.html'
    form_class = CourseRepeatingEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.course,
        })
        return kwargs


class CourseRepeatingEventUpdateView(CourseMixin, UpdateView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_event_form.html'
    form_class = CourseRepeatingEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.course,
        })
        return kwargs


class CourseRepeatingEventDeleteView(CourseMixin, DeleteView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/confirm_delete.html'

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.course.id})


class CourseSubmissionEventListView(CourseMixin, ListView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_events_list.html'
    paginate_by = 10


class CourseSubmissionEventCreateView(CourseMixin, CreateView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_event_form.html'
    form_class = CourseSubmissionEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.course,
        })
        return kwargs


class CourseSubmissionEventUpdateView(CourseMixin, UpdateView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_event_form.html'
    form_class = CourseSubmissionEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.course,
        })
        return kwargs


class CourseSubmissionEventDeleteView(CourseMixin, DeleteView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/confirm_delete.html'

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.course.id})
