from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Submission
from scheduler.models import Job


@receiver(post_save, sender=Submission)
def submit_job(sender, instance: Submission, created, **kwargs):
    job = Job.objects.create(submission=instance)
    job.save()
