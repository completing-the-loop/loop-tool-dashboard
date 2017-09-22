from decorator_include import decorator_include
from django.conf.urls import url

from django_site.permissions import course_access_url_wrapper
from olap.views import TopCourseUsersViewSet
from olap.views import PageVisitsViewSet

urlpatterns = [
    url(r'^(?P<course_id>\d+)/', decorator_include(course_access_url_wrapper, [
        url(r'^course_visits/$', PageVisitsViewSet.as_view(), name='course_visits'),
        url(r'^top_users/$', TopCourseUsersViewSet.as_view(), name='top_users'),
    ])),
]
