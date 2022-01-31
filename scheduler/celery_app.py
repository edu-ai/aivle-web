from __future__ import absolute_import

import os

from celery import Celery
from kombu import Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiVLE.settings')
app = Celery('aiVLE')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace="CELERY")
app.conf.task_default_queue = "default"
app.conf.task_queues = (
    Queue("default", routing_key="task.#"),
    Queue("gpu", routing_key="gpu.#"),
    Queue("private", routing_key="private.#"),
)


@app.task(bind=True, name="aiVLE.submit_eval_task")
def evaluate(self, job_id):
    pass
