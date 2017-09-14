from datetime import datetime
from datetime import timezone

from authtools.forms import AuthenticationForm
from django import forms
from django.forms import ValidationError
from django.forms.models import ModelForm

from dashboard.models import CourseRepeatingEvent
from dashboard.models import CourseSingleEvent
from dashboard.models import CourseSubmissionEvent


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'aria-required': 'true'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'aria-required': 'true' }))


class CourseRepeatingEventForm(ModelForm):
    class Meta:
        model = CourseRepeatingEvent
        fields = ['title', 'day_of_week', 'start_week', 'end_week']

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course')
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        self.instance.course = self.course
        return super().save(commit)

    def clean(self):
        super().clean()
        start_week = self.cleaned_data.get('start_week')
        end_week = self.cleaned_data.get('end_week')

        if start_week and end_week:
            if start_week < 1:
                self.add_error('start_week', ValidationError('Start week cannot be earlier than week 1'))
            if end_week > self.course.no_weeks:
                self.add_error('end_week', ValidationError('End week cannot be longer than the course length of {} weeks'.format(self.course.no_weeks)))
            if end_week < start_week:
                self.add_error('end_week', 'End week cannot be before start week')


class CourseSubmissionEventForm(ModelForm):
    class Meta:
        model = CourseSubmissionEvent
        fields = ['title', 'start_date', 'end_date', 'event_type']

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course')
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        self.instance.course = self.course
        return super().save(commit)

    def clean(self):
        super().clean()
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date:
            calc_end_date = self.course.get_end_date()
            course_start_date = datetime(self.course.start_date.year, self.course.start_date.month, self.course.start_date.day, tzinfo=timezone.utc)
            course_end_date = datetime(calc_end_date.year, calc_end_date.month, calc_end_date.day, tzinfo=timezone.utc)
            if start_date < course_start_date:
                self.add_error('start_date', ValidationError('Start date cannot be earlier than the start of the course'))
            if end_date > course_end_date:
                self.add_error('end_date', ValidationError('End date cannot be after the end of the course'))
            if end_date < start_date:
                self.add_error('end_date', 'End date cannot be before the start date')


class CourseSingleEventForm(ModelForm):
    class Meta:
        model = CourseSingleEvent
        fields = ['title', 'event_date']

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course')
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        self.instance.course = self.course
        return super().save(commit)

    def clean(self):
        super().clean()
        event_date = self.cleaned_data.get('event_date')

        if event_date:
            calc_end_date = self.course.get_end_date()
            course_start_date = datetime(self.course.start_date.year, self.course.start_date.month, self.course.start_date.day, tzinfo=timezone.utc)
            course_end_date = datetime(calc_end_date.year, calc_end_date.month, calc_end_date.day, tzinfo=timezone.utc)
            if event_date < course_start_date:
                self.add_error('event_date', ValidationError('Event date cannot be earlier than the start of the course'))
            if event_date > course_end_date:
                self.add_error('event_date', ValidationError('Event date cannot be after the end of the course'))
