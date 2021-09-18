# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('send', views.send_to_channel, name='send'),
    path('close', views.shutdown_worker_by_name, name='close'),
]  # TODO: remove test URLs
