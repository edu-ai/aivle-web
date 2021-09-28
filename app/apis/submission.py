import os

from django.contrib.auth.models import User
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from aiVLE.settings import ROLES_SUBMISSION_VIEW
from app.models import Submission, Task, Participation
from app.serializers import SubmissionSerializer
from app.utils.permission import has_perm


class SubmissionPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if not super(SubmissionPermissions, self).has_permission(request, view):
            return False
        if request.method in ["POST"]:
            if "task" not in request.data:
                return True  # hack
            task_id = request.data["task"]
            task = Task.objects.get(pk=task_id)
            if not task:
                return False
            if "user" not in request.data:  # user is inferred from credentials by default
                request.data["user"] = request.user.pk
            user_id = request.data["user"]  # this is to support DRF frontend behavior
            user = User.objects.get(pk=user_id)
            if not user or request.user != user:  # only allowed to submit on behalf of yourself
                return False
            return has_perm(task.course, request.user, "task.submit")
        return True

    def has_object_permission(self, request, view, obj: Submission):
        """Submission is immutable
        """
        return request.method in permissions.SAFE_METHODS


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [SubmissionPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "task"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Submission.objects.all()
        ptp = Participation.objects.filter(user__username=self.request.user.username)
        ptp_admin = ptp.filter(role__in=ROLES_SUBMISSION_VIEW)
        admin_courses = [i.course for i in ptp_admin]
        return Submission.objects.filter(user__username=self.request.user.username) | \
               Submission.objects.filter(task__course__in=admin_courses)

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        submission = self.get_object()
        if not has_perm(submission.task.course, request.user, "submission.download"):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        file_handle = submission.file.open()
        response = FileResponse(file_handle, content_type="application/octet-stream")
        response['Content-Length'] = submission.file.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(submission.file.name)
        return response
