from decorator_include import decorator_include
from django.conf.urls import url
from stronghold.decorators import public

from django_site.permissions import course_access_url_wrapper
from olap.views import CommunicationAccessesView
from olap.views import CommunicationEventsView
from olap.views import CommunicationPostsView
from olap.views import CommunicationStudentsView
from olap.views import CourseImportsApiView
from olap.views import PageVisitsViewSet
from olap.views import TopCourseUsersViewSet

urlpatterns = [
    # This endpoint is protected with Token Authentication
    url(r'^course_imports/$', public(CourseImportsApiView.as_view()), name='course_imports'),

    url(r'^(?P<course_id>\d+)/', decorator_include(course_access_url_wrapper, [
        url(r'^communication_accesses/$', CommunicationAccessesView.as_view(), name='communication_accesses'),
        url(r'^communication_posts/$', CommunicationPostsView.as_view(), name='communication_posts'),
        url(r'^communication_students/$', CommunicationStudentsView.as_view(), name='communication_students'),
        url(r'^communication_events/(?P<event_id>\d+)/$', CommunicationEventsView.as_view(), name='communication_events'),
        url(r'^course_visits/$', PageVisitsViewSet.as_view(), name='course_visits'),
        url(r'^top_users/$', TopCourseUsersViewSet.as_view(), name='top_users'),
    ])),
]
