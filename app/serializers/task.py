from rest_framework import serializers

from app.models import Task
from app.serializers import CourseSerializer


class TaskSerializer(serializers.ModelSerializer):
    grader_file_url = serializers.HyperlinkedIdentityField('task_grader_download', read_only=True)
    template_file_url = serializers.HyperlinkedIdentityField('template_download', read_only=True)
    grader = serializers.FileField(use_url=False)
    template = serializers.FileField(use_url=False, required=False)
    daily_submission_limit = serializers.IntegerField(default=3)
    max_upload_size = serializers.IntegerField(default=32)
    run_time_limit = serializers.IntegerField(default=600)

    class Meta:
        model = Task
        fields = "__all__"

    def to_representation(self, instance):
        response = super(TaskSerializer, self).to_representation(instance)
        response['course'] = CourseSerializer(instance.course).data["id"]
        return response