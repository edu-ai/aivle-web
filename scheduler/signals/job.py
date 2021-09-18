from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Submission
from scheduler.celery import evaluate
from scheduler.models import Job


@receiver(post_save, sender=Submission)
def submit_job(sender, instance: Submission, created, **kwargs):
    job = Job.objects.create(submission=instance)
    job.save()
    result = evaluate.delay(job_id=job.pk)
    job.task_id = result.id
    job.status = Job.STATUS_QUEUED
    job.save()
