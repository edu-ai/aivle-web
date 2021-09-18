from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiVLE.settings')
app = Celery('aiVLE')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace="CELERY")


@app.task(bind=True, name="aiVLE.submit_eval_task")
def evaluate(self, job_id):
    pass
