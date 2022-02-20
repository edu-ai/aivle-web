from rest_framework.serializers import ModelSerializer, SerializerMethodField

from app.models import Course, Participation
from app.serializers.participation import ParticipationSerializer


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CourseListSerializer(ModelSerializer):
    participation = SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "code", "academic_year", "semester", "visible", "participation")

    def get_participation(self, instance):
        user = self.context["request"].user
        participation = Participation.objects.filter(user=user, course=instance)
        if participation.exists():
            return ParticipationSerializer(participation.get()).data
        else:
            return None
