from rest_framework.fields import FileField, IntegerField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from app.models import Task, Course
from app.serializers import CourseSerializer


class CourseField(PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = Course.objects.all()
        if not request or not queryset:
            return None
        return queryset.filter(participants__username__contains=request.user.username)


class TaskSerializer(ModelSerializer):
    grader_file_url = HyperlinkedIdentityField('task_grader_download', read_only=True)
    template_file_url = HyperlinkedIdentityField('template_download', read_only=True)
    grader = FileField(use_url=False)
    template = FileField(use_url=False, required=False)
    daily_submission_limit = IntegerField(default=3)
    max_upload_size = IntegerField(default=32)
    run_time_limit = IntegerField(default=600)
    course = CourseField()

    class Meta:
        model = Task
        fields = "__all__"

    def to_representation(self, instance):
        response = super(TaskSerializer, self).to_representation(instance)
        response['course'] = CourseSerializer(instance.course).data["id"]
        return response
