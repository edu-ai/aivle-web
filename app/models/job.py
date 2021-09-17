from django.db import models

from app.models import Submission
from scheduler.models import Worker


class Job(models.Model):
    STATUS_QUEUED = 'Q'
    STATUS_RUNNING = 'R'
    STATUS_ERROR = 'E'
    STATUS_DONE = 'D'
    STATUSES = [
        (STATUS_QUEUED, 'Queued'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_ERROR, 'Error'),
        (STATUS_DONE, 'Done')
    ]

    worker = models.ForeignKey(Worker, null=True, on_delete=models.SET_NULL, related_name="jobs")
    worker_log = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=2, choices=STATUSES, default=STATUS_QUEUED)
