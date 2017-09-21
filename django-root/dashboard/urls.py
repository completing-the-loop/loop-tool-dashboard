from authtools.views import LogoutView
from django.conf.urls import url
from django.contrib.auth.views import logout
from stronghold.decorators import public

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
from dashboard.views.users import CustomLoginView
from dashboard.views.users import DashboardRedirectView

from dashboard.views import views


urlpatterns = [
    url(r'^$', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    url(r'^login/', public(CustomLoginView.as_view()), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^courses/', CourseListView.as_view(), name='course_list'),
    url(r'^(?P<course_id>\d+)/course_dashboard/$', CourseDashboardView.as_view(), name='course_dashboard'),

    # Event management for academic staff
    url(r'^(?P<course_id>\d+)/course_repeating_events/$', CourseRepeatingEventListView.as_view(), name='list_course_repeating_events'),
    url(r'^(?P<course_id>\d+)/course_repeating_event/$', CourseRepeatingEventCreateView.as_view(), name='add_course_repeating_event'),
    url(r'^(?P<course_id>\d+)/course_repeating_event/(?P<pk>\d+)/$', CourseRepeatingEventUpdateView.as_view(), name='edit_course_repeating_event'),
    url(r'^(?P<course_id>\d+)/course_repeating_event/(?P<pk>\d+)/delete/$', CourseRepeatingEventDeleteView.as_view(), name='delete_course_repeating_event'),
    url(r'^(?P<course_id>\d+)/course_submission_events/$', CourseSubmissionEventListView.as_view(), name='list_course_submission_events'),
    url(r'^(?P<course_id>\d+)/course_submission_event/$', CourseSubmissionEventCreateView.as_view(), name='add_course_submission_event'),
    url(r'^(?P<course_id>\d+)/course_submission_event/(?P<pk>\d+)/$', CourseSubmissionEventUpdateView.as_view(), name='edit_course_submission_event'),
    url(r'^(?P<course_id>\d+)/course_submission_event/(?P<pk>\d+)/delete/$', CourseSubmissionEventDeleteView.as_view(), name='delete_course_submission_event'),
    url(r'^(?P<course_id>\d+)/course_single_events/$', CourseSingleEventListView.as_view(), name='list_course_single_events'),
    url(r'^(?P<course_id>\d+)/course_single_event/$', CourseSingleEventCreateView.as_view(), name='add_course_single_event'),
    url(r'^(?P<course_id>\d+)/course_single_event/(?P<pk>\d+)/$', CourseSingleEventUpdateView.as_view(), name='edit_course_single_event'),
    url(r'^(?P<course_id>\d+)/course_single_event/(?P<pk>\d+)/delete/$', CourseSingleEventDeleteView.as_view(), name='delete_course_single_event'),

    url(r'^overallcoursedashboard/$', views.overallcoursedashboard, name='overallcoursedashboard'),
    url(r'^coursemembers/$', views.coursemembers, name='course_members'),
    url(r'^coursemember/$', views.coursemember, name='coursemember'),
    url(r'^coursepage/$', views.coursepage, name='coursepage'),
    url(r'^coursestructure/$', views.coursestructure, name='coursestructure'),
    url(r'^content/$', views.content, name='course_content'),
    url(r'^communication/$', views.communication, name='course_communications'),
    url(r'^assessment/$', views.assessment, name='course_assessments'),
    url(r'^pedagogyhelper/$', views.pedagogyhelper, name='pedagogyhelper'),
    url(r'^pedagogyhelperdownload/$', views.pedagogyhelperdownload, name='pedagogyhelperdownload'),
    url(r'^logout/$', logout,  {'next_page': '/home/'}, name='loggedout'),
]
