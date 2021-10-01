import uuid

from django.db import models
from app.models import Participation, Course

from django.utils import timezone


class Invitation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=3, choices=Participation.ROLES, default=Participation.ROLE_GUEST)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(null=False)
    valid_to = models.DateTimeField(null=False)
    valid = models.BooleanField(default=False)

    @property
    def is_valid(self):
        return self.valid and self.valid_from <= timezone.now() <= self.valid_to
