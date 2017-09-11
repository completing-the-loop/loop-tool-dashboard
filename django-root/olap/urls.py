from django.conf.urls import url

from olap.views import DimTopUserViewSet
from olap.views import FactCourseVisitsViewSet

urlpatterns = [
    url(r'^(?P<course_id>\d+)/course_visits/$', FactCourseVisitsViewSet.as_view(), name='course_visits'),
    url(r'^(?P<course_id>\d+)/top_users/$', DimTopUserViewSet.as_view(), name='top_users'),
]
