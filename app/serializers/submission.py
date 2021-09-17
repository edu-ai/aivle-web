from rest_framework import serializers

from app.models import Submission


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.HyperlinkedIdentityField('submission_download', read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'runner', 'metadata', 'docker', 'file_url', 'status', 'point', 'notes', 'task')