from django.contrib import admin

from dashboard.models import Course
from dashboard.models import CourseRepeatingEvent
from dashboard.models import CourseSingleEvent
from dashboard.models import CourseSubmissionEvent


admin.site.register(Course)
admin.site.register(CourseSubmissionEvent)
admin.site.register(CourseSingleEvent)
admin.site.register(CourseRepeatingEvent)
