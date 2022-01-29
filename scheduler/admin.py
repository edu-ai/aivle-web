from django.contrib import admin

from scheduler.models.job import Job
from scheduler.models.queue import Queue
from scheduler.models.worker import Worker

# Register your models here.
admin.site.register(Worker)  # Deprecated
admin.site.register(Job)
admin.site.register(Queue)
