from django.contrib.auth.models import User
from django.db import models


class Worker(models.Model):
    name = models.CharField(max_length=30)
    last_seen = models.DateTimeField(null=True)
    channel_name = models.CharField(max_length=256, default="")  # channel_name == "" means disconnected
