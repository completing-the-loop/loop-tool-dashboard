from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView

from dashboard.models import CourseOffering

from olap.models import LMSUser
from olap.models import PageVisit
from olap.serializers import PageVisitSerializer
from olap.serializers import TopCourseUsersSerializer


class PageVisitsViewSet(ListAPIView):
    serializer_class = PageVisitSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return PageVisit.objects.filter(course__id=course_id)


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer

    def get_queryset(self):
        course_offering = get_object_or_404(CourseOffering, pk=self.kwargs['course_id'])

        # FIXME: This used to have some hardcoded start/end date filtering here (1-Jan-14 to 31-Dec-16).  Do we still need it?
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=course_offering).order_by('-pageviews')[0:10]

        return qs

