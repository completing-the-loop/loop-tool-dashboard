from authtools.views import LogoutView
from django.conf.urls import url
from django.contrib.auth.views import logout
from stronghold.decorators import public

from dashboard import views


urlpatterns = [
    url(r'^$', views.DashboardRedirectView.as_view(), name='dashboard_redirect'),
    url(r'^login/', public(views.CustomLoginView.as_view()), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^courses/', views.CourseListView.as_view(), name='course_list'),

    url(r'^coursedashboard/$', views.coursedashboard, name='coursedashboard'),
    url(r'^overallcoursedashboard/$', views.overallcoursedashboard, name='overallcoursedashboard'),
    url(r'^coursemembers/$', views.coursemembers, name='coursemembers'),
    url(r'^coursemember/$', views.coursemember, name='coursemember'),
    url(r'^coursepage/$', views.coursepage, name='coursepage'),
    url(r'^content/$', views.content, name='content'),
    url(r'^coursestructure/$', views.coursestructure, name='coursestructure'),
    url(r'^communication/$', views.communication, name='communication'),
    url(r'^assessment/$', views.assessment, name='assessment'),
    url(r'^pedagogyhelper/$', views.pedagogyhelper, name='pedagogyhelper'),
    url(r'^pedagogyhelperdownload/$', views.pedagogyhelperdownload, name='pedagogyhelperdownload'),
    url(r'^logout/$', logout,  {'next_page': '/home/'}, name='loggedout'),
]
