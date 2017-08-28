from authtools.views import LogoutView
from django.conf.urls import url
from django.contrib.auth.views import logout
from stronghold.decorators import public

from dashboard.views.courses import CourseListView
from dashboard.views.dashboard import CourseDashboardView
from dashboard.views.users import CustomLoginView
from dashboard.views.users import DashboardRedirectView

from dashboard.views import views


urlpatterns = [
    url(r'^$', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    url(r'^login/', public(CustomLoginView.as_view()), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^courses/', CourseListView.as_view(), name='course_list'),
    url(r'^course_dashboard/$', CourseDashboardView.as_view(), name='course_dashboard'),

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
