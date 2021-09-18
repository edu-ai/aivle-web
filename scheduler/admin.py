from django.contrib import admin

from scheduler.models import Worker, Job

# Register your models here.
admin.site.register(Worker)
admin.site.register(Job)
