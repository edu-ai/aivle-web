import logging
import pickle
from ast import literal_eval

from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from app.models import Submission
from app.utils.permission import has_perm
from scheduler.models import Job
from scheduler.serializers import JobSerializer, JobListSerializer

logger = logging.getLogger('django')


class JobPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(JobPermissions, self).has_permission(request, view):
            return False
        if request.method not in SAFE_METHODS:
            return False  # read only permission
        return True

    def has_object_permission(self, request, view, obj: Job):
        if request.method not in SAFE_METHODS:
            return False  # read only permission
        return has_perm(obj.submission.task.course, request.user, "job.view")


class JobViewSet(ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    permission_classes = [JobPermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["submission"]
    ordering_fields = ["created_at", "updated_at"]

    def get_serializer_class(self, *args, **kwargs):
        """Instantiate the list of serializers per action from class attribute (must be defined)."""
        kwargs['partial'] = True
        if self.action == "list":
            return JobListSerializer
        return super(JobViewSet, self).get_serializer_class()

    @action(detail=True)
    def start_job(self, request, pk=None):
        if "task_id" not in request.data or "worker_name" not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "status": "failed",
                "reason": "fields `task_id` and `worker_name` must be present"
            })
        task_id = request.data["task_id"]
        worker_name = request.data["worker_name"]
        job = self.get_object()
        if job.task_id != task_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={
                "status": "failed",
                "reason": "incorrect task_id"
            })
        job.status = Job.STATUS_RUNNING
        job.worker_name = worker_name
        job.save()
        logger.info(f"task started: {task_id} on {worker_name}")
        return Response({
            "status": "success",
            "task": job.submission.task.pk,
            "submission": job.submission.pk,
        })

    @action(detail=True)
    def submit_job(self, request, pk=None):
        job = self.get_object()
        if job.status != Job.STATUS_RUNNING:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "status": "failed",
                "reason": "job is not running, please start job first"
            })
        if "task_id" not in request.data or "result" not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "status": "failed",
                "reason": "`task_id` and `result` must be present"
            })
        task_id = request.data["task_id"]  # IMPT: task_id refers to Task Queue ID, not aiVLE task ID
        result = request.data["result"]
        if job.task_id != task_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={
                "status": "failed",
                "reason": "incorrect task_id"
            })
        job.status = Job.STATUS_DONE
        job.worker_log = result
        try:  # TODO: no hack, support for >1 test cases
            obj = pickle.loads(literal_eval(result))
            score = obj["results"][0]["result"]["value"]
            other_submissions = Submission.objects.filter(task=job.submission.task, user=job.submission.user)
            prev_highest_score = other_submissions.aggregate(Max("point"))["point__max"]
            submission = job.submission
            submission.point = score
            submission.notes = str(obj)
            # By default, mark latest highest scoring submission for grading
            if prev_highest_score is None or prev_highest_score <= score:
                for other_submission in other_submissions:
                    other_submission.marked_for_grading = False
                Submission.objects.bulk_update(other_submissions, ["marked_for_grading"])
                submission.marked_for_grading = True
            submission.save()
            Submission.objects.aggregate(Max("point"))
        except Exception as e:
            logger.warning(e)
            pass
        job.save()
        logger.info(f"task finished: {task_id} by {job.worker_name}")
        return Response({
            "status": "success"
        })
