from django.db.models import Count
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

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
