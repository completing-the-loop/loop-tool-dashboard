import datetime

from django.db.models import Count
from rest_framework.generics import ListAPIView

from dashboard.models import CourseOffering
from olap.models import LMSUser
from olap.models import Page
from olap.models import SummaryPost
from olap.serializers import TopAccessedContentSerializer
from olap.serializers import TopCommunicationAccessSerializer
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


class TopCommunicationAccessView(ListAPIView):
    serializer_class = TopCommunicationAccessSerializer
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

        # Get the page list.  If only we could do all this at the db level.
        page_qs = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.COMMUNICATION_TYPES).values('id', 'title', 'content_type')

        # Augment all the pages with how many page views related to that page for the window of interest.
        for page in page_qs:
            page['pageviews'] = PageVisit.objects.filter(page=page['id'], visited_at__range=dt_range).count()

        # Sort by number of page views and trim down to top 10 rows
        # WARNING: This is messing with the internals of the query set
        page_qs._result_cache = sorted(page_qs._result_cache, key=lambda p: p['pageviews'], reverse=True)[0:self.max_rows_to_return]

        # Now calculate the data for the userviews and posts columns.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            # The userviews value is the number of distinct users to access this page in the time period.
            page['userviews'] = LMSUser.objects.filter(pagevisit__page=page['id'], pagevisit__visited_at__range=dt_range).distinct().count()
            # The posts value is the number of posts to this page in the window of interest.
            page['posts'] = SummaryPost.objects.filter(page=page['id'], posted_at__range=dt_range).count()

        return page_qs
