import datetime

from django.db.models import Avg
from django.db.models import Count
from rest_framework.generics import ListAPIView

from dashboard.models import CourseOffering
from olap.models import LMSUser
from olap.models import Page
from olap.models import SubmissionAttempt
from olap.serializers import TopAccessedContentSerializer
from olap.serializers import TopAssessmentAccessSerializer
from olap.serializers import TopCourseUsersSerializer


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:self.max_rows_to_return]

        return qs


class TopAccessedContentView(ListAPIView):
    serializer_class = TopAccessedContentSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        course_offering = self.request.course_offering
        # Was a week number specified? (week number is 1-based)
        week_num = self.kwargs.get('week_num')
        if week_num is not None:
            # Filter for pagevisits within the week
            range_start = course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
            range_end = range_start + datetime.timedelta(weeks=1)
        else:
            # Filter for pagevisits within the extent of the courseoffering
            range_start = course_offering.start_datetime
            range_end = range_start + datetime.timedelta(weeks=course_offering.no_weeks)
        dt_range = (range_start, range_end)

        # Get the page list.  pageviews can be done in the query.
        page_qs = Page.objects.filter(course_offering=course_offering, pagevisit__visited_at__range=dt_range).values('id', 'title', 'content_type').annotate(pageviews=Count("pagevisit")).order_by('-pageviews')[0:self.max_rows_to_return]

        # Now calculate the data for the userviews column by finding the number of distinct users to access each page in the time period.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            page['userviews'] = len(set(LMSUser.objects.filter(pagevisit__page=page['id'], pagevisit__visited_at__range=dt_range)))

        return page_qs


class TopAssessmentAccessView(ListAPIView):
    serializer_class = TopAssessmentAccessSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        course_offering = self.request.course_offering
        # Was a week number specified? (week number is 1-based)
        week_num = self.kwargs.get('week_num')
        if week_num is not None:
            # Filter for assessment accesses within the week
            range_start = course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
            range_end = range_start + datetime.timedelta(weeks=1)
        else:
            # Filter for assessment accesses within the extent of the courseoffering
            range_start = course_offering.start_datetime
            range_end = range_start + datetime.timedelta(weeks=course_offering.no_weeks)
        dt_range = (range_start, range_end)

        # Get the page list.  If only we could do all this at the db level.
        page_qs = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.ASSESSMENT_TYPES).values('id', 'title', 'content_type')

        # Augment all the pages with how many submission attempts related to that page for the window of interest.
        for page in page_qs:
            page['attempts'] = SubmissionAttempt.objects.filter(page=page['id'], attempted_at__range=dt_range).count()

        # Sort by number of submission attempts and trim down to top 10 rows
        # WARNING: This is messing with the internals of the query set
        page_qs._result_cache = sorted(page_qs._result_cache, key=lambda p: p['attempts'], reverse=True)[0:self.max_rows_to_return]

        # Now calculate the data for the userviews and average score columns.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            # The userviews value is the number of distinct users to make a submission attempt in the time period.
            page['userviews'] = LMSUser.objects.values('id').filter(submissionattempt__page=page['id'], submissionattempt__attempted_at__range=dt_range).distinct().count()
            # The average score is the average of scores for submission attempts in the time period.
            # FIXME: Check for average-related exceptions here.
            avg = SubmissionAttempt.objects.filter(page=page['id'], attempted_at__range=dt_range).aggregate(Avg('grade'))
            page['average_score'] = avg['grade__avg']

        return page_qs
