import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from aiVLE.settings import CELERY_ENABLE
from app.models import Submission
from scheduler.celery import evaluate
from scheduler.models import Job

logger = logging.getLogger('django')


@receiver(post_save, sender=Submission)
def submit_job(sender, instance: Submission, created, **kwargs):
    if not created:
        return  # prevent dead lock
    job = Job.objects.create(submission=instance)
    job.save()
    if CELERY_ENABLE:
        result = evaluate.apply_async(args=[job.pk], queue=instance.task.eval_queue)
        job.task_id = result.id
    else:
        job.task_id = "dummy_task_id"
    job.status = Job.STATUS_QUEUED
    job.save()
    logger.info(f"task {job.task_id} is submitted")
