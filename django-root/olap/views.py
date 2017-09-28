import datetime
from decimal import Decimal

from django.db.models import Count
from django.utils.timezone import get_current_timezone
from django.utils.timezone import make_aware

from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.serializers import CommunicationAccessesSerializer
from olap.serializers import PageVisitSerializer
from olap.serializers import TopCourseUsersSerializer
from olap.utils import get_course_import_metadata


class CourseImportsApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        api_data = get_course_import_metadata()
        return Response(api_data)


class PageVisitsViewSet(ListAPIView):
    serializer_class = PageVisitSerializer

    def get_queryset(self):
        return PageVisit.objects.filter(lms_user__course_offering=self.request.course_offering)


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:10]

        return qs


class CommunicationAccessesView(APIView):
    def get(self, request, format=None):
        course_offering = self.request.course_offering
        our_tz = get_current_timezone()
        course_start_dt = make_aware(datetime.datetime.combine(course_offering.start_date, datetime.time()), timezone=our_tz)

        visits_by_week_for_all_pages = [0] * course_offering.no_weeks
        page_queryset = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.COMMUNICATION_TYPES).values('id', 'title', 'content_type')
        total_visits = 0
        for page in page_queryset:
            visits_by_week_for_this_page = [0] * course_offering.no_weeks
            visits_to_this_page = PageVisit.objects.filter(page_id=page['id'])
            total_visits += visits_to_this_page.count()
            for visit in visits_to_this_page:
                # Calculate the time since start of course for this visit.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the isoweek boundary).
                td = visit.visited_at - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                visits_by_week_for_this_page[week] += 1
                visits_by_week_for_all_pages[week] += 1
            page['weeks'] = visits_by_week_for_this_page
            page['total'] = sum(visits_by_week_for_this_page)

        # Total page visits for all pages and weeks.  Will appear in bottom right corner.
        visits_by_week_for_all_pages.append(total_visits)
        # Calculate percentages.
        for page in page_queryset:
            page['percent'] = Decimal(page['total'] * 100 / total_visits)

        results = {
            'page_set': page_queryset,
            'totals_by_week': visits_by_week_for_all_pages,
        }

        serializer = CommunicationAccessesSerializer(data=results)
        # If we pass data to the serializer, we need to call .is_valid() before it's available in .data
        serializer.is_valid()
        sd = serializer.data

        return Response(sd)
