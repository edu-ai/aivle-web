from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from aiVLE.settings import ROLES_COURSE_VIEW_QUEUE
from app.utils.permission import has_perm
from scheduler.models.queue import Queue
from scheduler.serializers import QueueSerializer


class QueuePermissions(IsAuthenticated):
    def has_object_permission(self, request, view, obj: Queue):
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return has_perm(obj.course, request.user, "course.view_queue")
        else:
            return has_perm(obj.course, request.user, "course.edit_queue")


class QueueViewSet(ModelViewSet):
    serializer_class = QueueSerializer
    permission_classes = [QueuePermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Queue.objects.all()
        return Queue.objects.filter(course__participants__username__exact=self.request.user.username,
                                    course__participation__role__in=ROLES_COURSE_VIEW_QUEUE)
