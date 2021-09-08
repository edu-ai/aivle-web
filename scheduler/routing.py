# chat/routing.py
from django.urls import path, re_path

from . import consumers
from .consumers import ChatConsumer, WorkerConsumer

websocket_urlpatterns = [
    re_path(r'ws/worker/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    path("ws/v1/worker/register", WorkerConsumer.as_asgi())
]
