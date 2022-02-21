from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from app.models import Course
from app.utils.file_hash import task_grader_path, task_template_path
from scheduler.models.queue import Queue


class Task(models.Model):
    DEFAULT_MAX_UPLOAD_SIZE = 5 * 1024  # KiB
    DEFAULT_DAILY_SUBMISSIONS_LIMIT = 3
    DEFAULT_RUN_TIME_LIMIT = 60  # Second
    DEFAULT_RAM_LIMIT = 256  # MiB
    DEFAULT_VRAM_LIMIT = 256  # MiB

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    grader = models.FileField(upload_to=task_grader_path)
    template = models.FileField(upload_to=task_template_path, blank=True, null=True)

    daily_submission_limit = models.PositiveSmallIntegerField(default=DEFAULT_DAILY_SUBMISSIONS_LIMIT)
    max_upload_size = models.IntegerField(default=DEFAULT_MAX_UPLOAD_SIZE)  # in KiB
    run_time_limit = models.IntegerField(default=DEFAULT_RUN_TIME_LIMIT)
    ram_limit = models.IntegerField(default=DEFAULT_RAM_LIMIT)  # in MiB
    vram_limit = models.IntegerField(default=DEFAULT_VRAM_LIMIT)  # in MiB

    opened_at = models.DateTimeField(blank=True, null=True)
    deadline_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    # leaderboard = models.BooleanField(default=False)

    # parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subtasks', null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tasks')
    eval_queue = models.ForeignKey(Queue, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        This looks like a hack.
        Ref: https://stackoverflow.com/questions/52947136/how-to-call-my-field-validators-in-my-save-method-in-django
        """
        if self.eval_queue is not None and not self.eval_queue.public:
            if self.eval_queue.course != self.course:
                raise ValidationError("Evaluation queue needs to be either public or belongs to this task's course.")
        super(Task, self).save(*args, **kwargs)

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
