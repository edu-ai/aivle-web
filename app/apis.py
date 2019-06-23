from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Course, Task, Submission
from .funcs import serialize_submission


def jobs(request):
    submissions = Submission.objects.filter(status=Submission.STATUS_QUEUED).order_by('created_at').values('id')[:10]
    return JsonResponse({'jobs': list(submissions)})

def job_run(request, submission_pk):
    s = get_object_or_404(Submission, pk=submission_pk, status=Submission.STATUS_QUEUED)
    s.status = Submission.STATUS_RUNNING
    s.save()
    return JsonResponse(serialize_submission(s))

@csrf_exempt
def job_end(request, submission_pk):
    UPDATE_ALLOWED = ['verdict', 'point', 'notes', 'status']
    STATUS_ALLOWED = [Submission.STATUS_DONE, Submission.STATUS_ERROR]
    s = get_object_or_404(Submission, pk=submission_pk, status=Submission.STATUS_RUNNING)
    if request.method == 'POST' and request.content_type == 'application/json':
        json_data = json.loads(request.body)
        status = json_data.get('status')
        if status and status in STATUS_ALLOWED:
	        for key, value in json_data.items():
	            if key in UPDATE_ALLOWED:
	                setattr(s, key, value)
	        s.save()
    return JsonResponse(serialize_submission(s))