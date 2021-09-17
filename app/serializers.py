from rest_framework import serializers

from .models import Submission, Task, Similarity, User, Course


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('submission_download', read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'runner', 'metadata', 'docker', 'file_url', 'status', 'point', 'notes', 'task')


class TaskSerializer(serializers.ModelSerializer):
    grader_file_url = serializers.HyperlinkedIdentityField('task_grader_download', read_only=True)
    template_file_url = serializers.HyperlinkedIdentityField('template_download', read_only=True)
    grader = serializers.FileField(use_url=False)
    template = serializers.FileField(use_url=False)

    class Meta:
        model = Task
        fields = "__all__"

    def to_representation(self, instance):
        response = super(TaskSerializer, self).to_representation(instance)
        response['course'] = CourseSerializer(instance.course).data
        return response


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


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
