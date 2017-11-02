from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import LMSServer
from olap.utils import get_course_import_metadata


class CourseImportsApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        try:
            lms_server = LMSServer.objects.get(token=request.auth)
            api_data = get_course_import_metadata(lms_server)
            return Response(api_data)
        except LMSServer.DoesNotExist:
            raise NotFound()
