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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from aiVLE.settings import DOMAIN_NAME_PREFIX
from app import views
from app.apis import JobViewSet, TaskViewSet, SimilarityViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'similarities', SimilarityViewSet)
router.register(r'submissions', SubmissionViewSet)

urlpatterns = [
    url(r'^$', views.courses, name='home'),

    url(r'^courses/$', views.courses, name='courses'),
    url(r'^courses/new/$', views.course_add, name='course_add'),
    url(r'^courses/(?P<course_pk>\d+)/$', views.course, name='course'),
    url(r'^courses/(?P<course_pk>\d+)/delete/$', views.course_delete, name='course_delete'),
    url(r'^courses/(?P<course_pk>\d+)/join/$', views.course_join, name='course_join'),

    url(r'^courses/(?P<course_pk>\d+)/tasks/new/$', views.task_edit, name='task_new'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/edit/$', views.task_edit, name='task_edit'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/delete/$', views.task_delete, name='task_delete'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/leaderboard/$', views.leaderboard, name='leaderboard'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/stats/$', views.stats, name='stats'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/similarities/$', views.similarities, name='similarities'),

    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/submissions/$', views.submissions, name='submissions'),
    url(r'^courses/(?P<course_pk>\d+)/tasks/(?P<task_pk>\d+)/submissions/new/$', views.submission_new,
        name='submission_new'),

    url(r'^tasks/(?P<pk>\d+)/download/$', views.task_download, name='task_download'),
    url(r'^tasks/(?P<pk>\d+)/template/$', views.template_download, name='template_download'),
    url(r'^submissions/(?P<pk>\d+)/download/$', views.submission_download, name='submission_download'),
    url(r'^submissions/action/$', views.submissions_action, name='submissions_action'),

    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    url(r'^signup/$', views.signup, name='signup'),

    path('scheduler/', include('scheduler.urls')),  # TODO: remove test URLs
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
]

if DOMAIN_NAME_PREFIX is not None:
    urlpatterns = [path(DOMAIN_NAME_PREFIX, include(urlpatterns))]
