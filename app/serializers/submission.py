from datetime import datetime

from django.contrib.auth.models import User
from rest_framework.serializers import FileField, PrimaryKeyRelatedField, CurrentUserDefault, \
    ModelSerializer

from aiVLE.settings import ROLES_TASK_VIEW_ALL
from app.models import Submission, Task


class UserField(PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = User.objects.all()
        if not request or not queryset:
            return None
        return queryset.filter(username=request.user.username)


class TaskField(PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = Task.objects.all()
        if not request or not queryset:
            return None
        return queryset.filter(course__participants__username__contains=request.user.username,
                               course__participation__role__in=ROLES_TASK_VIEW_ALL) | \
               queryset.filter(course__participants__username__contains=request.user.username,
                               opened_at__lt=datetime.now())


class SubmissionSerializer(ModelSerializer):
    file = FileField(use_url=False)
    user = UserField(default=CurrentUserDefault())
    task = TaskField()

    class Meta:
        model = Submission
        fields = "__all__"
        read_only_fields = ('point', 'notes', 'marked_for_grading', 'created_at')
