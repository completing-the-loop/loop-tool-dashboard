from django.conf import settings
from django.db.models import Count

from rest_framework.generics import ListAPIView

from olap.models import DimUser
from olap.models import FactCourseVisit
from olap.serializers import DimTopUserSerializer
from olap.serializers import FactCourseVisitSerializer


class FactCourseVisitsViewSet(ListAPIView):
    serializer_class = FactCourseVisitSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return FactCourseVisit.objects.filter(course__id=course_id)


class DimTopUserViewSet(ListAPIView):
    serializer_class = DimTopUserSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']

        # FIXME: Need to limit visits by the duration of the course
        # FIXME: Need to filter by course_id.  Note should be course_id in factcoursevisit, not in dimuser
        # FIXME: I tried __in=(settings.DIMDATE_START, settings.DIMDATE_END) here, but the args got reversed
        qs = DimUser.objects.annotate(pageviews=Count("factcoursevisit")).filter(course_id=course_id, factcoursevisit__visited_at__gte=settings.DIMDATE_START, factcoursevisit__visited_at__lte=settings.DIMDATE_END).order_by('-pageviews')[0:10]

        return qs

