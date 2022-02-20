import os
from datetime import datetime
from itertools import groupby

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from aiVLE.settings import ROLES_TASK_VIEW_ALL
from app.models import Task, Course
from app.serializers import TaskSerializer, SimilaritySubmissionSerializer
from app.utils.permission import has_perm


class TaskPermissions(permissions.IsAuthenticated):
    def has_permission(self, request: Request, view):
        if not super(TaskPermissions, self).has_permission(request, view):
            return False
        if request.method in ["POST"]:
            if "course" not in request.data:
                return True  # hack
            course_id = request.data["course"]
            course = Course.objects.get(pk=course_id)
            if not course:
                return False
            return has_perm(course, request.user, "task.add")
        return True

    def has_object_permission(self, request, view, obj: Task):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            return has_perm(obj.course, request.user, "task.view")
        elif request.method == "POST":
            return has_perm(obj.course, request.user, "task.add")
        elif request.method == "PUT":
            return has_perm(obj.course, request.user, "task.edit")
        elif request.method == "DELETE":
            return has_perm(obj.course, request.user, "task.delete")
        else:
            return False


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["course"]
    ordering_fields = ["opened_at", "closed_at", "deadline_at"]
    search_fields = ["name", "description"]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        # TODO: consider using `can` for the following logic?
        return Task.objects.filter(course__participants__username__contains=self.request.user.username,
                                   opened_at__lt=datetime.now()) | \
               Task.objects.filter(course__participants__username__contains=self.request.user.username,
                                   course__participation__role__in=ROLES_TASK_VIEW_ALL)

    @action(detail=True, methods=["get"])
    def submissions_by_user(self, request, pk):
        if request.method == 'GET':
            task = Task.objects.get(pk=pk)
            submissions = task.submissions.all()
            key = lambda x: x.user
            grouped_submissions = groupby(sorted(submissions, key=lambda x: x.user.pk), key=key)
            result = {}
            for user, submissions in grouped_submissions:
                if has_perm(task.course, user, 'task.edit') or not user.is_active:
                    continue
                serializer = SimilaritySubmissionSerializer(submissions, many=True, context={'request': request})
                result[user.pk] = serializer.data
            return Response(result)

    @action(detail=True, methods=["get"])
    def download_grader(self, request, pk):
        task = self.get_object()
        if not has_perm(task.course, request.user, "task.download"):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        file_handle = task.grader.open()
        response = FileResponse(file_handle, content_type="application/zip")
        response['Content-Length'] = task.grader.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(task.grader.name)
        return response

    @action(detail=True, methods=["get"])
    def download_template(self, request, pk):
        task = self.get_object()
        if not has_perm(task.course, request.user, "task.download"):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not task.template:
            return Response(status=status.HTTP_404_NOT_FOUND)
        file_handle = task.template.open()
        response = FileResponse(file_handle, content_type="application/octet-stream")
        response['Content-Length'] = task.template.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(task.template.name)
        return response
