from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView

from dashboard.models import CourseOffering

from .models import LMSUser
from .models import FactCourseVisit
from .serializers import DimTopUserSerializer
from .serializers import FactCourseVisitSerializer


class FactCourseVisitsViewSet(ListAPIView):
    serializer_class = FactCourseVisitSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return FactCourseVisit.objects.filter(course__id=course_id)


class DimTopUserViewSet(ListAPIView):
    serializer_class = DimTopUserSerializer

    def get_queryset(self):
        course_offering = get_object_or_404(CourseOffering, pk=self.kwargs['course_id'])

        # FIXME: This used to have some hardcoded start/end date filtering here (1-Jan-14 to 31-Dec-16).  Do we still need it?
        qs = LMSUser.objects.annotate(pageviews=Count("factcoursevisit")).filter(course_offering=course_offering).order_by('-pageviews')[0:10]

        return qs

