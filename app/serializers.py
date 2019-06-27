from rest_framework import serializers
from .models import Submission, Task

class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('submission_download', read_only=True)
    class Meta:
        model = Submission
        fields = ('id', 'runner', 'metadata', 'file_url', 'status', 'point', 'notes', 'task')

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('task_download', read_only=True)
    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'file_url', 'file_hash', 'daily_submission_limit', 'max_upload_size', 'opened_at', 'closed_at', 'leaderboard')