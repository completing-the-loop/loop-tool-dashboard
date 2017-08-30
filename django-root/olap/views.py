from rest_framework.generics import ListAPIView

from olap.models import DimUser
from olap.models import FactCourseVisit
from olap.serializers import DimUserSerializer
from olap.serializers import FactCourseVisitSerializer


class FactCourseVisitsViewSet(ListAPIView):
    serializer_class = FactCourseVisitSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return FactCourseVisit.objects.filter(course__id=course_id)


class DimUserViewSet(ListAPIView):
    serializer_class = DimUserSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return DimUser.objects.filter(course__id=course_id)
