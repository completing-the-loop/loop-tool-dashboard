from rest_framework.generics import ListAPIView

from olap.models import FactCourseVisit
from olap.serializers import FactCourseVisitSerializer


class FactCourseVisitsViewSet(ListAPIView):
    serializer_class = FactCourseVisitSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return FactCourseVisit.objects.filter(course__id=course_id)
