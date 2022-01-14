from rest_framework.fields import FileField, IntegerField
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
    grader = FileField(use_url=False)
    template = FileField(use_url=False, required=False)
    daily_submission_limit = IntegerField(default=Task.DEFAULT_DAILY_SUBMISSIONS_LIMIT)
    max_upload_size = IntegerField(default=Task.DEFAULT_MAX_UPLOAD_SIZE)
    run_time_limit = IntegerField(default=Task.DEFAULT_RUN_TIME_LIMIT)
    course = CourseField()

    class Meta:
        model = Task
        fields = "__all__"

    def to_representation(self, instance):
        response = super(TaskSerializer, self).to_representation(instance)
        response['course'] = CourseSerializer(instance.course).data["id"]
        return response
