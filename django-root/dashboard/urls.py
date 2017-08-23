from django.conf.urls import url
from django.contrib.auth.views import logout

from dashboard import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^home/', views.home, name='home'),
    url(r'^mycourses/', views.mycourses, name='mycourses'),
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
