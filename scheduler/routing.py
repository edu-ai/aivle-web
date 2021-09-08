# chat/routing.py
from django.urls import path, re_path

from .consumers import WorkerConsumer

websocket_urlpatterns = [
    path("ws/v1/worker/register", WorkerConsumer.as_asgi())
]
