from django.db import models


class Worker(models.Model):
    """
    Deprecated implementation of WebSocket-based scheduler
    """
    name = models.CharField(max_length=30)
    last_seen = models.DateTimeField(null=True)
    channel_name = models.CharField(max_length=256, default="")  # channel_name == "" means disconnected
