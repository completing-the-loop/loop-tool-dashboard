from django.db.models import Count
from rest_framework.generics import ListAPIView

from olap.models import LMSUser
from olap.serializers import TopCourseUsersSerializer


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:10]

        return qs
