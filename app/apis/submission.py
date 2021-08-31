from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from app.models import Submission
from app.serializers import SubmissionSerializer


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (IsAdminUser,)