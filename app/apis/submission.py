from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets

from aiVLE.settings import ROLES_SUBMISSION_VIEW
from app.utils.permission import can
from app.models import Submission, Task, Participation
from app.serializers import SubmissionSerializer


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
            user_id = request.data["user"]
            user = User.objects.get(pk=user_id)
            if not user or request.user != user:  # only allowed to submit on behalf of yourself
                return False
            return can(task.course, request.user, "task.submit")
        return True

    def has_object_permission(self, request, view, obj: Submission):
        """Submission is immutable
        """
        return request.method in permissions.SAFE_METHODS


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [SubmissionPermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Submission.objects.all()
        ptp = Participation.objects.filter(user__username=self.request.user.username)
        ptp_admin = ptp.filter(role__in=ROLES_SUBMISSION_VIEW)
        admin_courses = [i.course for i in ptp_admin]
        return Submission.objects.filter(user__username=self.request.user.username) | \
               Submission.objects.filter(task__course__in=admin_courses)
