from django.urls.base import reverse
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from dashboard.forms import CourseRepeatingEventForm
from dashboard.forms import CourseSingleEventForm
from dashboard.forms import CourseSubmissionEventForm
from dashboard.models import CourseRepeatingEvent
from dashboard.models import CourseSingleEvent
from dashboard.models import CourseSubmissionEvent


class CourseRepeatingEventListView(ListView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_events_list.html'
    paginate_by = 10


class CourseRepeatingEventCreateView(CreateView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_event_form.html'
    form_class = CourseRepeatingEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.request.course_offering})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseRepeatingEventUpdateView(UpdateView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/course_repeating_event_form.html'
    form_class = CourseRepeatingEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.request.course_offering.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseRepeatingEventDeleteView(DeleteView):
    model = CourseRepeatingEvent
    template_name = 'dashboard/confirm_delete.html'

    def get_success_url(self):
        return reverse('dashboard:list_course_repeating_events', kwargs={'course_id': self.request.course_offering.id})


class CourseSubmissionEventListView(ListView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_events_list.html'
    paginate_by = 10


class CourseSubmissionEventCreateView(CreateView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_event_form.html'
    form_class = CourseSubmissionEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.request.course_offering.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseSubmissionEventUpdateView(UpdateView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/course_submission_event_form.html'
    form_class = CourseSubmissionEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.request.course_offering.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseSubmissionEventDeleteView(DeleteView):
    model = CourseSubmissionEvent
    template_name = 'dashboard/confirm_delete.html'

    def get_success_url(self):
        return reverse('dashboard:list_course_submission_events', kwargs={'course_id': self.request.course_offering.id})


class CourseSingleEventListView(ListView):
    model = CourseSingleEvent
    template_name = 'dashboard/course_single_events_list.html'
    paginate_by = 10


class CourseSingleEventCreateView(CreateView):
    model = CourseSingleEvent
    template_name = 'dashboard/course_single_event_form.html'
    form_class = CourseSingleEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_single_events', kwargs={'course_id': self.request.course_offering.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseSingleEventUpdateView(UpdateView):
    model = CourseSingleEvent
    template_name = 'dashboard/course_single_event_form.html'
    form_class = CourseSingleEventForm

    def get_success_url(self):
        return reverse('dashboard:list_course_single_events', kwargs={'course_id': self.request.course_offering.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'course': self.request.course_offering,
        })
        return kwargs


class CourseSingleEventDeleteView(DeleteView):
    model = CourseSingleEvent
    template_name = 'dashboard/confirm_delete.html'

    def get_success_url(self):
        return reverse('dashboard:list_course_single_events', kwargs={'course_id': self.request.course_offering.id})
