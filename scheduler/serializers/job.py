from rest_framework.serializers import ModelSerializer

from scheduler.models.job import Job


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "worker_name", "status", "error", "worker_log", "created_at", "updated_at")


class JobListSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "worker_name", "status", "error")
