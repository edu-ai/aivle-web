from rest_framework.serializers import ModelSerializer, SerializerMethodField

from app.models import Course


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CourseListSerializer(ModelSerializer):
    participating = SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "code", "academic_year", "semester", "visible", "participating")

    def get_participating(self, instance):
        user = self.context["request"].user
        course = instance
        return user in course.participants.all()
