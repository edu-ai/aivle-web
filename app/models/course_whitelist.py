from django.contrib.auth.models import User
from django.db import models

from app.models import Course


class CourseWhitelist(models.Model):
    class Meta:
        unique_together = (('course', 'email'),)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='whitelisted_emails')
    email = models.EmailField()

    def __str__(self):
        return f"{self.course} - {self.email}"
