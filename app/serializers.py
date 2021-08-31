from rest_framework import serializers

from .models import Submission, Task, Similarity, User


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('submission_download', read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'runner', 'metadata', 'docker', 'file_url', 'status', 'point', 'notes', 'task')


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('task_download', read_only=True)
    template_url = serializers.HyperlinkedIdentityField('template_download', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'name', 'description', 'file_url', 'file_hash', 'template_url', 'template_file',
            'daily_submission_limit',
            'max_upload_size', 'run_time_limit', 'max_image_size', 'opened_at', 'closed_at', 'leaderboard')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class SimilaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Similarity
        fields = ('id', 'user', 'task', 'submission', 'related', 'score', 'diff')


class SimilaritySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'user', 'task', 'point')
