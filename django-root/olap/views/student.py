from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from olap.models import Page
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.models import SummaryPost
from olap.serializers import StudentAssessmentSerializer
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


class StudentAssessmentView(APIView):

    def get(self, request, student_id, format=None):
        assessments = Page.objects.filter(course_offering=self.request.course_offering, content_type__in=CourseOffering.assessment_types()).values('id', 'title', 'content_type')

        for assessment in assessments:
            assessment['user_views'] = PageVisit.objects.filter(lms_user_id=student_id, page_id=assessment['id']).count()
            attempts = SubmissionAttempt.objects.filter(lms_user_id=student_id, page_id=assessment['id']).values_list('grade', flat=True)
            assessment['attempts'] = len(attempts)
            assessment['average_grade'] = Decimal(sum(attempts) / assessment['attempts']) if assessment['attempts'] else 0

        serializer = StudentAssessmentSerializer(data=assessments, many=True)
        sd = serializer.initial_data

        return Response(sd)
