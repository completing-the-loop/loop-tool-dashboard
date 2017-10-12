import datetime

from django.db.models import Count
from django.db.models import Q
from rest_framework.generics import ListAPIView

from olap.models import LMSUser
from olap.models import Page
from olap.serializers import TopAccessedContentSerializer
from olap.serializers import TopCourseUsersSerializer


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:10]

        return qs


class TopAccessedContentView(ListAPIView):
    serializer_class = TopAccessedContentSerializer

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
        page_qs = Page.objects.filter(course_offering=course_offering, pagevisit__visited_at__range=dt_range).values('id', 'title', 'content_type').annotate(pageviews=Count("pagevisit")).order_by('-pageviews')[0:10]

        # Now calculate the data for the userviews column by finding the number of distinct users to access each page in the time period.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            page['userviews'] = len(set(LMSUser.objects.filter(pagevisit__page=page['id'], pagevisit__visited_at__range=dt_range)))

        return page_qs
