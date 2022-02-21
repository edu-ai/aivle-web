import datetime
import os

from django.contrib.auth.models import User
from django.http import FileResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from aiVLE.settings import ROLES_SUBMISSION_VIEW
from app.models import Submission, Task, Participation
from app.serializers import SubmissionSerializer
from app.utils.permission import has_perm
from scheduler.signals import create_job_with_submission


class SubmissionLimitExceeded(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You have exceeded your daily submission limit.')
    default_code = 'submission_limit_exceeded'


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
                request.data["user"] = request.user.pk  # TODO: this line is invalid and causes trouble sometimes
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


class SubmissionBeforeDeadlinePermissions(permissions.IsAuthenticated):
    message = "Submitting after deadline is not allowed."
    code = 403

    def has_permission(self, request, view):
        if not super(SubmissionBeforeDeadlinePermissions, self).has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True  # do whatever you want, superuser...
        if request.method in ["POST"]:
            if "task" not in request.data:
                return True  # hack
            task_id = request.data["task"]
            task = Task.objects.get(pk=task_id)
            if not task:
                return False
            return timezone.now() <= task.deadline_at  # enforce submit deadline
        return True


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [SubmissionPermissions, SubmissionBeforeDeadlinePermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "task", "marked_for_grading"]
    ordering_fields = ["created_at"]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        current_datetime = datetime.datetime.now()
        daily_submission_count = Submission.objects.filter(user_id=request.data["user"],
                                                           created_at__year=current_datetime.year,
                                                           created_at__month=current_datetime.month,
                                                           created_at__day=current_datetime.day).count()
        task = Task.objects.get(pk=request.data["task"])
        if daily_submission_count >= task.daily_submission_limit:
            raise SubmissionLimitExceeded()
        return super(SubmissionViewSet, self).create(request, *args, **kwargs)

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

    @action(methods=["get"], detail=True)
    def mark_for_grading(self, request, pk):
        submission = self.get_object()
        if has_perm(submission.task.course, request.user, "submission.mark") \
                or request.user == submission.user:
            submissions = Submission.objects.filter(user=submission.user, task=submission.task)
            for other_submission in submissions:
                other_submission.marked_for_grading = False
            Submission.objects.bulk_update(submissions, ["marked_for_grading"])
            submission.marked_for_grading = True
            submission.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=["get"], detail=True)
    def rerun(self, request, pk):
        submission = self.get_object()
        if has_perm(submission.task.course, request.user, "submission.rerun"):
            create_job_with_submission(submission)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
