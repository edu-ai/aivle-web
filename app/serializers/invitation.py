from rest_framework.serializers import ModelSerializer

from app.models import Invitation
from app.serializers.task import CourseField


class InvitationSerializer(ModelSerializer):
    course = CourseField()

    class Meta:
        model = Invitation
        fields = "__all__"
        read_only_fields = ("valid", )
