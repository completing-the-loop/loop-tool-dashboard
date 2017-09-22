from django.db.models import Count

from rest_framework.generics import ListAPIView

from olap.models import LMSUser
from olap.models import PageVisit
from olap.serializers import PageVisitSerializer
from olap.serializers import TopCourseUsersSerializer


class PageVisitsViewSet(ListAPIView):
    serializer_class = PageVisitSerializer

    def get_queryset(self):
        return PageVisit.objects.filter(lms_user__course_offering=self.request.course_offering)


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:10]

        return qs
