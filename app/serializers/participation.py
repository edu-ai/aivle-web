from rest_framework.serializers import ModelSerializer

from app.models import Participation


class ParticipationSerializer(ModelSerializer):
    class Meta:
        model = Participation
        fields = "__all__"
        read_only_fields = ("user", "course")
