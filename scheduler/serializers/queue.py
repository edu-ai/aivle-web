from rest_framework.serializers import ModelSerializer

from scheduler.models.queue import Queue


class QueueSerializer(ModelSerializer):
    class Meta:
        model = Queue
        fields = "__all__"
