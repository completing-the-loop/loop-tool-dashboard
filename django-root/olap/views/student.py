from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from olap.models import Page
from olap.models import PageVisit
from olap.models import SummaryPost
from olap.serializers import StudentCommunicationSerializer


class StudentCommunicationView(APIView):

    def get(self, request, student_id, format=None):
        communications = Page.objects.filter(course_offering=self.request.course_offering, content_type__in=CourseOffering.communication_types()).values('id', 'title', 'content_type')

        for communication in communications:
            communication['user_views'] = PageVisit.objects.filter(lms_user_id=student_id, page_id=communication['id']).count()
            communication['posts'] = SummaryPost.objects.filter(lms_user_id=student_id, page_id=communication['id']).count()

        serializer = StudentCommunicationSerializer(data=communications, many=True)
        sd = serializer.initial_data

        return Response(sd)


