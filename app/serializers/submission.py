from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedIdentityField, FileField, PrimaryKeyRelatedField, CurrentUserDefault, \
    ModelSerializer

from app.models import Submission


class SubmissionSerializer(ModelSerializer):
    download_url = HyperlinkedIdentityField('submission_download', read_only=True)
    file = FileField(use_url=False)
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), default=CurrentUserDefault())

    class Meta:
        model = Submission
        fields = "__all__"
