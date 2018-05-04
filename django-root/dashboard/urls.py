from authtools.views import LogoutView
from decorator_include import decorator_include
from django.conf.urls import url
from stronghold.decorators import public

from dashboard.views.assessment import CourseAssessmentView
from dashboard.views.communication import CourseCommunicationView
from dashboard.views.content import CourseContentView
from dashboard.views.content import ResourcePageView
from dashboard.views.courses import CourseListView
from dashboard.views.dashboard import CourseDashboardView
from dashboard.views.events import CourseRepeatingEventCreateView
from dashboard.views.events import CourseRepeatingEventDeleteView
from dashboard.views.events import CourseRepeatingEventListView
from dashboard.views.events import CourseRepeatingEventUpdateView
from dashboard.views.events import CourseSingleEventCreateView
from dashboard.views.events import CourseSingleEventDeleteView
from dashboard.views.events import CourseSingleEventListView
from dashboard.views.events import CourseSingleEventUpdateView
from dashboard.views.events import CourseSubmissionEventCreateView
from dashboard.views.events import CourseSubmissionEventDeleteView
from dashboard.views.events import CourseSubmissionEventListView
from dashboard.views.events import CourseSubmissionEventUpdateView
from dashboard.views.students import StudentDetailView
from dashboard.views.students import StudentsView
from dashboard.views.users import CustomLoginView
from dashboard.views.users import DashboardRedirectView
from django_site.permissions import course_access_url_wrapper


urlpatterns = [
    url(r'^$', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    url(r'^login/', public(CustomLoginView.as_view()), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^courses/', CourseListView.as_view(), name='course_list'),

    url(r'^(?P<course_id>\d+)/', decorator_include(course_access_url_wrapper, [
        url(r'^course_dashboard/$', CourseDashboardView.as_view(), name='course_dashboard'),
        url(r'^assessment/$', CourseAssessmentView.as_view(), name='course_assessments'),
        url(r'^communication/$', CourseCommunicationView.as_view(), name='course_communications'),
        url(r'^course_content/$', CourseContentView.as_view(), name='course_content'),
        url(r'^students/$', StudentsView.as_view(), name='students'),
        url(r'^student/(?P<pk>\d+)/$', StudentDetailView.as_view(), name='student_detail'),
        url(r'^course_page/(?P<pk>\d+)/$', ResourcePageView.as_view(), name='course_page'),

        # Event management for academic staff
        url(r'^course_repeating_events/$', CourseRepeatingEventListView.as_view(), name='list_course_repeating_events'),
        url(r'^course_repeating_event/$', CourseRepeatingEventCreateView.as_view(), name='add_course_repeating_event'),
        url(r'^course_repeating_event/(?P<pk>\d+)/$', CourseRepeatingEventUpdateView.as_view(), name='edit_course_repeating_event'),
        url(r'^course_repeating_event/(?P<pk>\d+)/delete/$', CourseRepeatingEventDeleteView.as_view(), name='delete_course_repeating_event'),
        url(r'^course_submission_events/$', CourseSubmissionEventListView.as_view(), name='list_course_submission_events'),
        url(r'^course_submission_event/$', CourseSubmissionEventCreateView.as_view(), name='add_course_submission_event'),
        url(r'^course_submission_event/(?P<pk>\d+)/$', CourseSubmissionEventUpdateView.as_view(), name='edit_course_submission_event'),
        url(r'^course_submission_event/(?P<pk>\d+)/delete/$', CourseSubmissionEventDeleteView.as_view(), name='delete_course_submission_event'),
        url(r'^course_single_events/$', CourseSingleEventListView.as_view(), name='list_course_single_events'),
        url(r'^course_single_event/$', CourseSingleEventCreateView.as_view(), name='add_course_single_event'),
        url(r'^course_single_event/(?P<pk>\d+)/$', CourseSingleEventUpdateView.as_view(), name='edit_course_single_event'),
        url(r'^course_single_event/(?P<pk>\d+)/delete/$', CourseSingleEventDeleteView.as_view(), name='delete_course_single_event'),
    ])),
]
