from datetime import datetime
from itertools import groupby

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from aiVLE.settings import ROLES_TASK_VIEW_ALL, ROLES_TASK_VIEW
from app.funcs import can
from app.models import Task, Participation, Course
from app.serializers import TaskSerializer, SimilaritySubmissionSerializer


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
            return can(course, request.user, "task.add")
        return True

    def has_object_permission(self, request, view, obj: Task):
        if request.method in permissions.SAFE_METHODS:
            return can(obj.course, request.user, "task.view")
        elif request.method == "POST":
            return can(obj.course, request.user, "task.add")
        elif request.method == "PUT":
            return can(obj.course, request.user, "task.edit")
        elif request.method == "DELETE":
            return can(obj.course, request.user, "task.delete")
        else:
            return False


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        # TODO: consider using `can` for the following logic?
        ptp = Participation.objects.filter(user__username=self.request.user.username)
        ptp_admin = ptp.filter(role__in=ROLES_TASK_VIEW_ALL)
        ptp_normal = ptp.filter(role__in=ROLES_TASK_VIEW)
        normal_course_ids = [i.course.id for i in ptp_normal]
        admin_course_ids = [i.course.id for i in ptp_admin]
        return Task.objects.filter(course_id__in=normal_course_ids).filter(opened_at__lt=datetime.now()) | \
               Task.objects.filter(course_id__in=admin_course_ids)

    @action(detail=True, methods=['get'])
    def submissions_by_user(self, request, pk):
        if request.method == 'GET':
            task = Task.objects.get(pk=pk)
            submissions = task.submissions.all()
            key = lambda x: x.user
            grouped_submissions = groupby(sorted(submissions, key=lambda x: x.user.pk), key=key)
            result = {}
            for user, submissions in grouped_submissions:
                if can(task.course, user, 'task.edit') or not user.is_active:
                    continue
                serializer = SimilaritySubmissionSerializer(submissions, many=True, context={'request': request})
                result[user.pk] = serializer.data
            return Response(result)
