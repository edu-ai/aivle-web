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
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from aiVLE.settings import DOMAIN_NAME_PREFIX
from app import views
from app.apis import TaskViewSet, SubmissionViewSet, CourseViewSet
from scheduler.apis import JobViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename="jobs")
router.register(r'tasks', TaskViewSet, basename="tasks")
router.register(r'submissions', SubmissionViewSet, basename="submissions")
router.register(r'courses', CourseViewSet, basename="courses")

urlpatterns = [
    path('', lambda req: redirect('api/v1/')),

    url(r'^tasks/(?P<pk>\d+)/download/$', views.task_grader_download, name='task_grader_download'),
    url(r'^tasks/(?P<pk>\d+)/template/$', views.template_download, name='template_download'),
    url(r'^submissions/(?P<pk>\d+)/download/$', views.submission_download, name='submission_download'),

    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('scheduler/', include('scheduler.urls')),  # TODO: remove test URLs
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
]

if DOMAIN_NAME_PREFIX is not None:
    urlpatterns = [path(DOMAIN_NAME_PREFIX, include(urlpatterns))]
