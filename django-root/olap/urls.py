from decorator_include import decorator_include
from django.conf.urls import url
from stronghold.decorators import public

from django_site.permissions import course_access_url_wrapper
from olap.views.assessment import AssessmentAccessesView
from olap.views.assessment import AssessmentEventsView
from olap.views.assessment import AssessmentGradesView
from olap.views.assessment import AssessmentStudentsView
from olap.views.common import CoursePageVisitsView
from olap.views.common import StudentPageVisitsView
from olap.views.communication import CommunicationAccessesView
from olap.views.communication import CommunicationEventsView
from olap.views.communication import CommunicationPostsView
from olap.views.communication import CommunicationStudentsView
from olap.views.content import ContentAccessesView
from olap.views.content import ContentEventsView
from olap.views.content import ContentStudentsView
from olap.views.content import StudentsNotViewedResourceView
from olap.views.dashboard import PerWeekMetricsView
from olap.views.dashboard import PerWeekPageVisitsView
from olap.views.dashboard import TopAccessedContentView
from olap.views.dashboard import TopAssessmentAccessView
from olap.views.dashboard import TopCommunicationAccessView
from olap.views.dashboard import TopCourseUsersViewSet
from olap.views.importer import CourseImportsApiView
from olap.views.student import StudentAssessmentView
from olap.views.student import StudentCommunicationView
from olap.views.students import StudentsAccessesView
from olap.views.students import StudentsEventsView

urlpatterns = [
    # This endpoint is protected with Token Authentication
    url(r'^course_imports/$', public(CourseImportsApiView.as_view()), name='course_imports'),

    url(r'^(?P<course_id>\d+)/', decorator_include(course_access_url_wrapper, [
        url(r'^assessment_accesses/$', AssessmentAccessesView.as_view(), name='assessment_accesses'),
        url(r'^assessment_grades/$', AssessmentGradesView.as_view(), name='assessment_grades'),
        url(r'^assessment_students/$', AssessmentStudentsView.as_view(), name='assessment_students'),
        url(r'^assessment_events/(?P<event_id>\d+)/$', AssessmentEventsView.as_view(), name='assessment_events'),

        url(r'^communication_accesses/$', CommunicationAccessesView.as_view(), name='communication_accesses'),
        url(r'^communication_posts/$', CommunicationPostsView.as_view(), name='communication_posts'),
        url(r'^communication_students/$', CommunicationStudentsView.as_view(), name='communication_students'),
        url(r'^communication_events/(?P<event_id>\d+)/$', CommunicationEventsView.as_view(), name='communication_events'),

        url(r'^content_accesses/$', ContentAccessesView.as_view(), name='content_accesses'),
        url(r'^content_students/$', ContentStudentsView.as_view(), name='content_students'),
        url(r'^content_events/(?P<event_id>\d+)/$', ContentEventsView.as_view(), name='content_events'),

        url(r'^students_accesses/$', StudentsAccessesView.as_view(), name='students_accesses'),
        url(r'^students_events/(?P<event_id>\d+)/$', StudentsEventsView.as_view(), name='students_events'),

        url(r'^student_assessments/(?P<student_id>\d+)/$', StudentAssessmentView.as_view(), name='student_assessments'),
        url(r'^student_communications/(?P<student_id>\d+)/$', StudentCommunicationView.as_view(), name='student_communications'),

        url(r'^course_page_visits/$', CoursePageVisitsView.as_view(), name='course_page_visits'),
        url(r'^student_page_visits/$', StudentPageVisitsView.as_view(), name='student_page_visits'),

        url(r'^top_assessments/(?:(?P<week_num>\d+)/)?$', TopAssessmentAccessView.as_view(), name='top_assessment'), # optional week
        url(r'^top_communication/(?:(?P<week_num>\d+)/)?$', TopCommunicationAccessView.as_view(), name='top_communication'), # optional week
        url(r'^top_content/(?:(?P<week_num>\d+)/)?$', TopAccessedContentView.as_view(), name='top_content'), # optional week
        url(r'^top_users/$', TopCourseUsersViewSet.as_view(), name='top_users'),

        url(r'^weekly_page_visits/(?P<week_num>\d+)/$', PerWeekPageVisitsView.as_view(), name='per_week_page_visits'),
        url(r'^weekly_metrics/(?P<week_num>\d+)/$', PerWeekMetricsView.as_view(), name='per_week_metrics'),

        url(r'^resource/(?P<resource_id>\d+)/not_viewed_students/$', StudentsNotViewedResourceView.as_view(), name='students_not_viewed_resource'),

    ])),
]
