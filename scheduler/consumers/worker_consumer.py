import json

from channels.generic.websocket import AsyncWebsocketConsumer


class WorkerConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        print(self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.send(
            self.channel_name,
            {
                "type": "chat_message",
                "message": text_data
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
