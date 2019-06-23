"""aiVLE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from app import views, apis

urlpatterns = [
    url(r'^$', views.courses, name='home'),

    url(r'^courses/$', views.courses, name='courses'),
    url(r'^courses/new/$', views.course_add, name='course_add'),
    url(r'^courses/(?P<course_pk>\d+)/$', views.course, name='course'),
    url(r'^courses/(?P<course_pk>\d+)/delete$', views.course_delete, name='course_delete'),
    url(r'^courses/(?P<course_pk>\d+)/join$', views.course_join, name='course_join'),

    url(r'^courses/(?P<course_pk>\d+)/tasks/new/$', views.task_edit, name='task_new'),
	url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/edit/$', views.task_edit, name='task_edit'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/delete/$', views.task_delete, name='task_delete'),

    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/submissions/$', views.submissions, name='submissions'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/submissions/new/$', views.submission_new, name='submission_new'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/leaderboard/$', views.leaderboard, name='leaderboard'),


    url(r'^api/v1/jobs/$', apis.jobs, name='jobs'),
    url(r'^api/v1/jobs/(?P<submission_pk>\d+)/run/$', apis.job_run, name='job_run'),
    url(r'^api/v1/jobs/(?P<submission_pk>\d+)/end/$', apis.job_end, name='job_done'),


    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]
