"""
Deprecated implementation of WebSocket-based scheduler
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse

from scheduler.models.worker import Worker


def send_to_channel(request):
    channel_name = request.GET.get("channel_name")
    message = request.GET.get("message")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        channel_name,
        {
            "type": "chat_message",
            "message": message
        }
    )
    return JsonResponse(data={
        "status": "success"
    })


def shutdown_worker_by_name(request):
    worker_name = request.GET.get("name")
    w = Worker.objects.get(name=worker_name)
    async_to_sync(get_channel_layer().send)(
        w.channel_name,
        {
            "type": "worker.close"
        }
    )
    return JsonResponse(data={
        "status": "success"
    })
