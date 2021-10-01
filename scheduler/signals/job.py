from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Submission
from scheduler.celery import evaluate
from scheduler.models import Job


@receiver(post_save, sender=Submission)
def submit_job(sender, instance: Submission, created, **kwargs):
    if not created:
        return  # prevent dead lock
    job = Job.objects.create(submission=instance)
    job.save()
    result = evaluate.apply_async(args=[job.pk], queue=instance.task.eval_queue)
    job.task_id = result.id
    job.status = Job.STATUS_QUEUED
    job.save()
