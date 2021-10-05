from rest_framework.serializers import ModelSerializer, SerializerMethodField

from app.models import CourseWhitelist
from app.serializers import CourseField


class CourseWhitelistSerializer(ModelSerializer):
    course = CourseField()

    class Meta:
        model = CourseWhitelist
        fields = "__all__"
