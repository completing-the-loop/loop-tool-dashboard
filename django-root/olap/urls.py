from decorator_include import decorator_include
from django.conf.urls import url
from stronghold.decorators import public

from django_site.permissions import course_access_url_wrapper
from olap.views.communication import CommunicationAccessesView
from olap.views.communication import CommunicationEventsView
from olap.views.communication import CommunicationPostsView
from olap.views.communication import CommunicationStudentsView
from olap.views.content import ContentAccessesView
from olap.views.content import ContentEventsView
from olap.views.content import ContentStudentsView
from olap.views.dashboard import TopAccessedContentView
from olap.views.dashboard import TopCourseUsersViewSet
from olap.views.importer import CourseImportsApiView

urlpatterns = [
    # This endpoint is protected with Token Authentication
    url(r'^course_imports/$', public(CourseImportsApiView.as_view()), name='course_imports'),

    url(r'^(?P<course_id>\d+)/', decorator_include(course_access_url_wrapper, [
        url(r'^communication_accesses/$', CommunicationAccessesView.as_view(), name='communication_accesses'),
        url(r'^communication_posts/$', CommunicationPostsView.as_view(), name='communication_posts'),
        url(r'^communication_students/$', CommunicationStudentsView.as_view(), name='communication_students'),
        url(r'^communication_events/(?P<event_id>\d+)/$', CommunicationEventsView.as_view(), name='communication_events'),

        url(r'^content_accesses/$', ContentAccessesView.as_view(), name='content_accesses'),
        url(r'^content_students/$', ContentStudentsView.as_view(), name='content_students'),
        url(r'^content_events/(?P<event_id>\d+)/$', ContentEventsView.as_view(), name='content_events'),

        url(r'^top_users/$', TopCourseUsersViewSet.as_view(), name='top_users'),
        url(r'^top_content/(?:(?P<week_num>\d+)/)?$', TopAccessedContentView.as_view(), name='top_content'), # optional week
    ])),
]
