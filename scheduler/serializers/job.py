from rest_framework.serializers import ModelSerializer

from scheduler.models import Job


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "worker_name", "status", "worker_log",)


class JobListSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "worker_name", "status",)
