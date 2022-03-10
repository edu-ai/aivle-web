from django.db import models

from app.models import Submission


class Job(models.Model):
    STATUS_RECEIVED = 'C'
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

    ERROR_TIME_LIMIT_EXCEEDED = "TLE"
    ERROR_MEMORY_LIMIT_EXCEEDED = "MLE"
    ERROR_VRAM_LIMIT_EXCEEDED = "VLE"
    ERROR_RUNTIME_ERROR = "RE"
    ERRORS = [
        (ERROR_TIME_LIMIT_EXCEEDED, "Time Limit Exceeded"),
        (ERROR_MEMORY_LIMIT_EXCEEDED, "Memory Limit Exceeded"),
        (ERROR_VRAM_LIMIT_EXCEEDED, "VRAM Limit Exceeded"),
        (ERROR_RUNTIME_ERROR, "Runtime Error"),
    ]

    # worker = models.ForeignKey(Worker, null=True, on_delete=models.SET_NULL, related_name="jobs")
    worker_name = models.CharField(max_length=64, null=True)
    worker_log = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=2, choices=STATUSES, default=STATUS_QUEUED)
    error = models.CharField(max_length=4, choices=ERRORS, null=True)
    task_id = models.CharField(max_length=64, null=True)  # Celery task/job ID, NOT aiVLE task ID

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
            return f"Job - {self.worker_name} - {status_desc} - {self.error} - {self.submission_id}"
        else:
            return f"Job - NO_WORKER - {status_desc} - {self.error} - {self.submission_id}"
