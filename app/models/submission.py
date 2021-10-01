import json
import os
import re

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from app.models.task import Task
from app.utils.file_hash import submission_path


class Submission(models.Model):
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=submission_path, blank=True, null=True)

    metadata = models.TextField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')

    point = models.DecimalField(max_digits=9, decimal_places=3, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    marked_for_grading = models.BooleanField(default=False)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else None

    @property
    def file_url(self):
        return reverse('submission_download', args=(self.task.course.pk, self.task.pk, self.pk))

    @property
    def file_size(self):
        try:
            return self.file.size
        except:
            return None

    @property
    def info(self):
        try:
            if self.notes is not None:
                notes = self.notes.replace('\\n', ' ')
                for er in ['Error', 'Exception', 'error']:
                    if er in notes:
                        return re.findall(r'(\w*%s\w*)' % er, notes)[-1]  # return the last one
            return json.loads(self.notes)['error']['type']
        except:
            return self.point

    @property
    def is_late(self):
        if self.task.deadline:
            return self.created_at > self.task.deadline
        return False

    def __str__(self):
        return "{}:{} - {} - {} AY{} Sem{}".format(self.user, self.pk, self.task.name,
                                                   self.task.course.code, self.task.course.academic_year,
                                                   self.task.course.semester)
