from django.contrib import admin
from .models import Course, Task, Submission, Participation

admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(Participation)