from rest_framework import serializers
from .models import Submission

class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'runner', 'metadata', 'file', 'status', 'verdict', 'point', 'notes')