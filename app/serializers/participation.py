from rest_framework.serializers import ModelSerializer

from app.models import Participation


class ParticipationSerializer(ModelSerializer):
    class Meta:
        model = Participation
        fields = "__all__"
