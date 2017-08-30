from django.conf.urls import url

from olap.views import DimUserViewSet
from olap.views import FactCourseVisitsViewSet

urlpatterns = [
    url(r'^(?P<course_id>\d+)/course_visits/$', FactCourseVisitsViewSet.as_view(), name='course_visits'),
    url(r'^(?P<course_id>\d+)/course_users/$', DimUserViewSet.as_view(), name='course_users'),
]
