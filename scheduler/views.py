from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


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
