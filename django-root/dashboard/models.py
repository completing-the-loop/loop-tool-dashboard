from authtools.models import User
from django.db import models


class Course(models.Model):
    LMS_TYPE_BLACKBOARD = 'blackboard'
    LMS_TYPE_MOODLE = 'moodle'
    LMS_TYPE_CHOICES = (
        (LMS_TYPE_BLACKBOARD, 'Blackboard'),
        (LMS_TYPE_MOODLE, 'Moodle'),
    )

    code = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    offering = models.CharField(max_length=255)
    owner = models.ManyToManyField(User)
    start_date = models.DateField()
    no_weeks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    lms_type = models.CharField(max_length=50, choices=LMS_TYPE_CHOICES, default=LMS_TYPE_BLACKBOARD)

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
    course = models.ForeignKey(Course)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default=EVENT_TYPE_ASSIGNMENT, blank=True)

    def __str__(self):
        return self.title


class CourseSingleEvent(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course)
    event_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class CourseRepeatingEvent(models.Model):
    EVENT_DAY_MON = '0'
    EVENT_DAY_TUE = '1'
    EVENT_DAY_WED = '2'
    EVENT_DAY_THU = '3'
    EVENT_DAY_FRI = '4'
    EVENT_DAY_SAT = '5'
    EVENT_DAY_SUN = '6'
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
    course = models.ForeignKey(Course)
    start_week = models.IntegerField(blank=True)
    end_week = models.IntegerField(blank=True)
    day_of_week = models.CharField(max_length=50, choices=EVENT_DAY_CHOICES, default=EVENT_DAY_MON)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PedagogyHelper(models.Model):
    pedagogyhelper_json = models.TextField(blank=False)
    course = models.ForeignKey(Course)
