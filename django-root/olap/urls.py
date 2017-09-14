from django.conf.urls import url

from olap.views import TopCourseUsersViewSet
from olap.views import PageVisitsViewSet

urlpatterns = [
    url(r'^(?P<course_id>\d+)/course_visits/$', PageVisitsViewSet.as_view(), name='course_visits'),
    url(r'^(?P<course_id>\d+)/top_users/$', TopCourseUsersViewSet.as_view(), name='top_users'),
]
