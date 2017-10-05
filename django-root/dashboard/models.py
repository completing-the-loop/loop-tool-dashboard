from datetime import datetime
import pytz

from authtools.models import User
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


class CourseOffering(models.Model):
    LMS_TYPE_BLACKBOARD = 'blackboard'
    LMS_TYPE_MOODLE = 'moodle'
    LMS_TYPE_CHOICES = (
        (LMS_TYPE_BLACKBOARD, 'Blackboard'),
        (LMS_TYPE_MOODLE, 'Moodle'),
    )

    code = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    offering = models.CharField(max_length=255)
    owners = models.ManyToManyField(User)
    start_date = models.DateField()
    no_weeks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    lms_type = models.CharField(max_length=50, choices=LMS_TYPE_CHOICES, default=LMS_TYPE_BLACKBOARD)
    last_activity_at = models.DateTimeField(blank=True, null=True)  # The last recorded page visit, submission attempt or summary post
    is_importing = models.BooleanField(default=False)

    @property
    def end_date(self):
        return self.start_date + timedelta(weeks=self.no_weeks)

    def get_weeks(self):
        start_week = self.start_date.isocalendar()[1]
        end_week = self.end_date.isocalendar()[1]
        return list(range(start_week, end_week))

    @property
    def start_datetime(self):
        local_tz = pytz.timezone(settings.TIME_ZONE)

        return timezone.make_aware(datetime(
            self.start_date.year,
            self.start_date.month,
            self.start_date.day
        ), local_tz)

    @property
    def end_datetime(self):
        local_tz = pytz.timezone(settings.TIME_ZONE)
        end_date = self.end_date

        return timezone.make_aware(datetime(
            end_date.year,
            end_date.month,
            end_date.day
        ), local_tz)

    def get_last_activity_date(self):
        last_activity_at = self.last_activity_at
        if not last_activity_at:
            last_activity_at = self.start_datetime
        return last_activity_at

    def __str__(self):
        return self.code


class CourseSubmissionEvent(models.Model):
    EVENT_TYPE_ASSIGNMENT = 'assignment'
    EVENT_TYPE_QUIZ = 'quiz'
    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_ASSIGNMENT, 'Assignment'),
        (EVENT_TYPE_QUIZ, 'Quiz'),
    )

    title = models.CharField(max_length=255)
    course_offering = models.ForeignKey(CourseOffering)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default=EVENT_TYPE_ASSIGNMENT)

    def get_event_type(self):
        return dict(self.EVENT_TYPE_CHOICES)[self.event_type]

    def __str__(self):
        return self.title


class CourseSingleEvent(models.Model):
    title = models.CharField(max_length=255)
    course_offering = models.ForeignKey(CourseOffering)
    event_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class CourseRepeatingEvent(models.Model):
    EVENT_DAY_MON = 0
    EVENT_DAY_TUE = 1
    EVENT_DAY_WED = 2
    EVENT_DAY_THU = 3
    EVENT_DAY_FRI = 4
    EVENT_DAY_SAT = 5
    EVENT_DAY_SUN = 6
    EVENT_DAY_CHOICES = (
        (EVENT_DAY_MON, 'Monday'),
        (EVENT_DAY_TUE, 'Tuesday'),
        (EVENT_DAY_WED, 'Wednesday'),
        (EVENT_DAY_THU, 'Thursday'),
        (EVENT_DAY_FRI, 'Friday'),
        (EVENT_DAY_SAT, 'Saturday'),
        (EVENT_DAY_SUN, 'Sunday'),
    )

    title = models.CharField(max_length=255)
    course_offering = models.ForeignKey(CourseOffering)
    start_week = models.IntegerField()
    end_week = models.IntegerField()
    day_of_week = models.IntegerField(choices=EVENT_DAY_CHOICES, default=EVENT_DAY_MON)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_event_day(self):
        return dict(self.EVENT_DAY_CHOICES)[self.day_of_week]

    def __str__(self):
        return self.title


class PedagogyHelper(models.Model):
    pedagogyhelper_json = models.TextField(blank=False)
    course_offering = models.ForeignKey(CourseOffering)
