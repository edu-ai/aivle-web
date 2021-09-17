from rest_framework import serializers

from app.models import Similarity, Submission


class SimilaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Similarity
        fields = ('id', 'user', 'task', 'submission', 'related', 'score', 'diff')


class SimilaritySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'user', 'task', 'point')