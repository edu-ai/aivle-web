from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from app.models import Course


class Queue(models.Model):
    name = models.CharField(max_length=64, unique=True)
    public = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    cpu_required = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )  # CPU required in percentage
    ram_required = models.IntegerField()  # RAM requried in MiB
    vram_required = models.IntegerField()  # VRAM required in MiB

    def __str__(self):
        return self.name
