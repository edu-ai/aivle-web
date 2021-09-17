from django.db import models
from django.urls import reverse
from django.utils import timezone

from app.models import Course
from app.utils.file_hash import task_grader_path, task_template_path


class Task(models.Model):
    DEFAULT_MAX_UPLOAD_SIZE = 5 * 1024  # KB
    DEFAULT_DAILY_SUBMISSIONS_LIMIT = 3
    DEFAULT_RUN_TIME_LIMIT = 60  # Second

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # file = ExtraFileField(upload_to=task_grader_path, after_file_save=compute_file_hash)
    # file_hash = models.CharField(max_length=255)

    grader = models.FileField(upload_to=task_grader_path)
    template = models.FileField(upload_to=task_template_path, blank=True, null=True)

    daily_submission_limit = models.PositiveSmallIntegerField(default=DEFAULT_DAILY_SUBMISSIONS_LIMIT)
    max_upload_size = models.IntegerField(default=DEFAULT_MAX_UPLOAD_SIZE)
    run_time_limit = models.IntegerField(default=DEFAULT_RUN_TIME_LIMIT)

    opened_at = models.DateTimeField(blank=True, null=True)
    deadline_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    # leaderboard = models.BooleanField(default=False)

    # parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subtasks', null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tasks')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def deadline(self):
        if self.deadline_at:
            return self.deadline_at
        return self.closed_at

    @property
    def is_open(self):
        if self.opened_at and self.opened_at > timezone.now():
            return False
        if self.is_dead:
            return False
        return True

    @property
    def is_late(self):
        return self.deadline_at and self.deadline_at < timezone.now()

    @property
    def is_dead(self):
        return self.closed_at and self.closed_at < timezone.now()

    def get_status_display(self):
        if self.is_dead:
            return "Closed"
        if self.is_late:
            return "Ended"
        return "Open" if self.is_open else "Scheduled"

    @property
    def file_url(self):
        return reverse('task_grader_download', args=(self.course.pk, self.pk))

    def __str__(self):
        return "{} - {} AY{} Sem{}".format(self.name, self.course.code, self.course.academic_year, self.course.semester)
