from django.db import models

from app.models import Submission
from scheduler.models import Worker


class Job(models.Model):
    STATUS_RECEIVED = 'R'
    STATUS_QUEUED = 'Q'
    STATUS_RUNNING = 'R'
    STATUS_ERROR = 'E'
    STATUS_DONE = 'D'
    STATUSES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_QUEUED, 'Queued'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_ERROR, 'Error'),
        (STATUS_DONE, 'Done')
    ]

    # worker = models.ForeignKey(Worker, null=True, on_delete=models.SET_NULL, related_name="jobs")
    worker_name = models.CharField(max_length=64, null=True)
    worker_log = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=2, choices=STATUSES, default=STATUS_QUEUED)
    task_id = models.CharField(max_length=64, null=True)

    def __str__(self):
        if self.worker:
            return f"Job - {self.worker_name} - {self.status} - {self.submission_id}"
        else:
            return f"Job - NO_WORKER - {self.status} - {self.submission_id}"
