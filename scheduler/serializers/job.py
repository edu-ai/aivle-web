from rest_framework.serializers import ModelSerializer

from scheduler.models import Job


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
        
