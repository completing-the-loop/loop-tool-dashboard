from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from olap.utils import get_course_import_metadata


class CourseImportsApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        api_data = get_course_import_metadata()
        return Response(api_data)
