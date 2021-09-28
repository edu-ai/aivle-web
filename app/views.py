import os
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse

from aiVLE.settings import FRONTEND_URL
from .models import Task, Submission
from .utils.permission import has_perm


@login_required
def task_grader_download(request, pk):
    task = get_object_or_404(Task, pk=pk)
    redirect_url = reverse('course', args=(task.course.pk,))

    if not has_perm(task.course, request.user, 'task.download'):
        messages.error(request, 'You are not allowed to download this task.')
        return redirect(redirect_url)

    filename = os.path.basename(task.grader.name)
    response = HttpResponse(task.grader, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


@login_required
def template_download(request, pk):
    task = get_object_or_404(Task, pk=pk)
    redirect_url = reverse('course', args=(task.course.pk,))

    if not has_perm(task.course, request.user, 'task.view'):
        messages.error(request, 'You are not allowed to download this template.')
        return redirect(redirect_url)

    filename = os.path.basename(task.template.name)
    response = HttpResponse(task.template, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


@login_required
def submission_download(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    redirect_url = reverse('submissions', args=(submission.task.course.pk, submission.task.pk))

    if not has_perm(submission.task.course, request.user, 'submission.download', submission=submission):
        messages.error(request, 'You are not allowed to download this submission.')
        return redirect(redirect_url)

    filename = os.path.basename(submission.file.name)
    response = HttpResponse(submission.file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


def handle_verify_email(request, key):
    params = urlencode({"key": key})
    return redirect(f"{FRONTEND_URL}/account/verify_email/?{params}")


def handle_reset_password(request, uid, token):
    params = urlencode({"uid": uid, "token": token})
    return redirect(f"{FRONTEND_URL}/account/reset_password_confirm/?{params}")
