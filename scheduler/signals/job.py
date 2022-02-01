import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from aiVLE.settings import CELERY_ENABLE
from app.models import Submission
from scheduler.celery_app import evaluate
from scheduler.models.job import Job

logger = logging.getLogger('django')


@receiver(post_save, sender=Submission)
def create_job_upon_submission(sender, instance: Submission, created, **kwargs):
    if not created:
        return  # prevent dead lock
    create_job_with_submission(instance)


def create_job_with_submission(submission: Submission):
    job = Job.objects.create(submission=submission)
    job.save()
    if CELERY_ENABLE:
        result = evaluate.apply_async(args=[job.pk], queue=submission.task.eval_queue.name)
        job.task_id = result.id
    else:
        job.task_id = "dummy_task_id"
    job.status = Job.STATUS_QUEUED
    job.save()
    logger.info(f"{job} created for {submission}")
