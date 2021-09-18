from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from scheduler.models import Job
from scheduler.serializers import JobSerializer


class JobViewSet(ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()

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
        task_id = request.data["task_id"]
        result = request.data["result"]
        if job.task_id != task_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={
                "status": "failed",
                "reason": "incorrect task_id"
            })
        job.status = Job.STATUS_DONE
        job.worker_log = result
        job.save()
        return Response({
            "status": "success"
        })
