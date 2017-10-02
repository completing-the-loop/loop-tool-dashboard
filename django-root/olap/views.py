from datetime import datetime

import pytz
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from olap.models import LMSUser
from olap.models import PageVisit
from olap.serializers import PageVisitSerializer
from olap.serializers import TopCourseUsersSerializer


class CourseExportsApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        course_offerings = []
        for course_offering in CourseOffering.objects.filter(is_importing=False):
            last_activity_at = course_offering.last_activity_at
            if not last_activity_at:
                local_tz = pytz.timezone(settings.TIME_ZONE)
                last_activity_at = timezone.make_aware(datetime(course_offering.start_date.year, course_offering.start_date.month, course_offering.start_date.day), local_tz)

            course_offerings.append({
                'course_code': course_offering.code,
                'last_activity': last_activity_at,
            })

        api_data = {
            'import_location': settings.DATA_IMPORT_DIR,
            'courses': course_offerings
        }
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
