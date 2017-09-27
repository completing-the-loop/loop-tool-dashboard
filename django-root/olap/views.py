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
from olap.models import PageVisit
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
        our_tz = get_current_timezone()
        course_offering = self.request.course_offering
        course_start_dt = make_aware(datetime.datetime.combine(course_offering.start_date, datetime.time()), timezone=our_tz)

        # Get "communications"-type page visits for this course, sorted by page.  Sorting by page is important.
        visit_queryset = PageVisit.objects.filter(page__course_offering=course_offering,
                                        page__content_type__in=CourseOffering.COMMUNICATION_TYPES).order_by('page', 'visited_at')
        visits_by_page_and_week = []
        visits_by_week_for_this_page = [0] * course_offering.no_weeks
        visits_by_week_for_all_pages = [0] * course_offering.no_weeks
        prev_page = None
        this_page = None
        total_visits_for_this_page = 0
        for visit in visit_queryset:
            this_page = visit.page
            if this_page != prev_page: # Are the visits switching from one page to the next (visits are in page order)
                if prev_page: # We're switching pages.  Have info for previous page?  False if it's the first page.
                    page_info = {
                        'id': prev_page.id,
                        'title': prev_page.title,
                        'module': prev_page.content_type,
                        'weeks': visits_by_week_for_this_page,
                        'total': total_visits_for_this_page,
                    }
                    visits_by_page_and_week.append(page_info)
                    # Reset counters ready for the new page
                    total_visits_for_this_page = 0
                    visits_by_week_for_this_page = [0] * course_offering.no_weeks
                prev_page = this_page
            total_visits_for_this_page += 1
            # Calculate the time since start of course for this visit.  From this we can calculate the week.
            # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
            # be the same as the isoweek boundary).
            td = visit.visited_at - course_start_dt
            week = td.days // 7 # Integer division, the first week after the course starts is week 0.
            visits_by_week_for_this_page[week] += 1
            visits_by_week_for_all_pages[week] += 1

        if this_page: # False if there were no visits, no pages, or both.  In that case, don't save.
            page_info = {
                'id': this_page.id,
                'title': this_page.title,
                'module': this_page.content_type,
                'weeks': visits_by_week_for_this_page,
                'total': total_visits_for_this_page,
            }
            visits_by_page_and_week.append(page_info)

        # Total page visits for all pages and weeks.  Will appear in bottom right corner.
        total_visits = len(visit_queryset)
        visits_by_week_for_all_pages.append(total_visits)
        # Calculate percentages.
        for page in visits_by_page_and_week:
            page['percent'] = Decimal(page['total'] * 100 / total_visits)

        results = {
            'page_set': visits_by_page_and_week,
            'totals_by_week': visits_by_week_for_all_pages,
        }

        # Since we're returning a dict (rather than ORM instances which need serialisation), we don't use a Serializer.
        return Response(results)
