import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from aiVLE.settings import ROLES_COURSE_VIEW_QUEUE
from app.utils.permission import has_perm
from scheduler.celery_app import app
from scheduler.models.queue import Queue
from scheduler.serializers import QueueSerializer

logger = logging.getLogger('django')


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

    worker_param = openapi.Parameter('worker', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                                     description='Celery worker name')

    @action(detail=True, methods=["get"])
    @swagger_auto_schema(manual_parameters=[worker_param])
    def stop_consuming(self, request, pk):
        if "worker" not in request.query_params:
            return Response(data={"reason": "no worker found in param"},
                            status=status.HTTP_400_BAD_REQUEST)
        queue = self.get_object()
        worker = request.query_params["worker"]
        logger.info(f"stop consuming from {queue} in {worker}")
        logger.info(app.control.cancel_consumer(queue.name, destination=[worker], reply=True))
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(manual_parameters=[worker_param])
    @action(detail=True, methods=["get"])
    def resume_consuming(self, request, pk):
        if "worker" not in request.query_params:
            return Response(data={"reason": "no worker found in param"},
                            status=status.HTTP_400_BAD_REQUEST)
        queue = self.get_object()
        worker = request.query_params["worker"]
        logger.info(f"resume consuming from {queue} in {worker}")
        logger.info(app.control.add_consumer(queue.name, destination=[worker], reply=True))
        return Response(status=status.HTTP_200_OK)
