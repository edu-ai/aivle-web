from django.db import models

from app.models import Submission


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def _get_status_description(status_char: str):
        for item in Job.STATUSES:
            if item[0] == status_char:
                return item[1]
        return "Unknown"

    def __str__(self):
        status_desc = self._get_status_description(self.status)
        if self.worker_name:
            return f"Job - {self.worker_name} - {status_desc} - {self.submission_id}"
        else:
            return f"Job - NO_WORKER - {status_desc} - {self.submission_id}"
