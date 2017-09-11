from authtools.forms import AuthenticationForm
from django import forms
from django.forms import ValidationError
from django.forms.models import ModelForm

from dashboard.models import CourseRepeatingEvent


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
