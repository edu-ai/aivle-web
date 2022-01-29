import json
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from scheduler.models.worker import Worker


class WorkerConsumer(AsyncWebsocketConsumer):
    """
    Deprecated implementation of WebSocket-based scheduler
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        print(self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.remove_worker(channel_name=self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            obj = json.loads(text_data)
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "worker." + obj["method"],
                    "obj": obj
                }
            )
        except KeyError:
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "worker.error",
                    "message": 'a field named "method" should be present in the request body'
                }
            )
        except Exception as e:
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "worker.error",
                    "message": str(e)
                }
            )

    async def worker_error(self, event):
        await self.send(text_data=json.dumps({
            "type": "response",
            "success": False,
            "reason": event["message"]
        }))

    async def worker_register(self, event):
        obj = event["obj"]
        await self.add_worker(name=obj["name"], channel_name=self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "response",
            "success": True,
            "channel_name": self.channel_name
        }))

    async def worker_heartbeat(self, event):
        await self.update_worker_last_seen(channel_name=self.channel_name)

    async def worker_close(self, event):
        await self.send(text_data=json.dumps({
            "type": "request",
            "method": "close"
        }))

    async def worker_assign(self, event):
        await self.send(text_data=json.dumps({
            "type": "request",
            "method": "assign"
        }))

    @database_sync_to_async
    def add_worker(self, name: str, channel_name: str) -> int:
        w = Worker(name=name, last_seen=datetime.now(), channel_name=channel_name)
        w.save()
        return w.id

    @database_sync_to_async
    def remove_worker(self, channel_name: str):
        Worker.objects.filter(channel_name=channel_name).delete()

    @database_sync_to_async
    def update_worker_last_seen(self, channel_name: str):
        w = Worker.objects.get(channel_name=channel_name)
        w.last_seen = datetime.now()
        w.save()
