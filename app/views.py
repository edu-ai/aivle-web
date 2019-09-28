from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Max
from django.http import HttpResponse
from django.contrib.auth import login, authenticate

from .models import Course, Task, Submission, Participation
from .forms import TaskForm, SubmissionForm, CourseForm, RegisterForm
from .funcs import can, submission_is_allowed, course_participations, course_participation

import os


@login_required
def courses(request):
    return render(request, 'courses.html', {'course_participations': course_participations(request.user, with_form=True)})

@login_required
def course_join(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    redirect_url = reverse('courses')
    cp = course_participation(request.user, course)

    if cp.joined:
        messages.error(request, 'You already joined the course.')
        return redirect(redirect_url)

    if not can(course, request.user, 'course.join', participation=cp.participation):
        messages.error(request, 'You can\'t join this course.')
        return redirect(redirect_url)

    participation = Participation(user=request.user, course=course, role=cp.participation.role)
    participation.save()
    return redirect(reverse('courses'))

@login_required
def course_add(request):
    redirect_url = reverse('courses')

    course = Course()
    form = CourseForm(request.POST or None, instance=course)

    if request.POST and form.is_valid():
        cp = course_participation(request.user, form.instance)

        if cp.added:
            messages.error(request, 'The course is already added.')
            return redirect(redirect_url)

        if not can(course, request.user, 'course.add', participation=cp.participation):
            messages.error(request, 'You are not allowed to add course.')
            return redirect(redirect_url)

        form.save()

        participation = Participation(user=request.user, course=course, role=cp.participation.role)
        participation.save()

    return redirect(redirect_url)

@login_required
def course_delete(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    cp = course_participation(request.user, course)

    if not can(course, request.user, 'course.delete', participation=cp.participation):
        messages.error(request, 'You can\'t delete this course.')
    else:
        course.delete()

    return redirect(reverse('courses'))

@login_required
def course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can(course, request.user, 'course.view'):
        messages.error(request, 'You are not participating in this course.')
        return redirect(reverse('courses'))

    return render(request, 'course.html', {'course': course})

@login_required
def task_edit(request, course_pk, task_pk=None):
    course = get_object_or_404(Course, pk=course_pk)

    if not can(course, request.user, 'task.edit'):
        messages.error(request, 'You are not allowed to {} task.'.format('edit' if task_pk else 'add'))
        return redirect(reverse('course', args=(course_pk,)))

    if task_pk:
        task = get_object_or_404(Task, pk=task_pk)
    else:
        task = Task(course=course)

    form = TaskForm(request.POST or None, request.FILES or None, instance=task)
    if request.POST and form.is_valid():
        form.save()

        redirect_url = reverse('course', args=(course_pk,))
        return redirect(redirect_url)

    return render(request, 'task_edit.html', {'form': form})

@login_required
def task_delete(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)

    if not can(task.course, request.user, 'task.delete'):
        messages.error(request, 'You are not allowed to delete this task.')
    else:
        task.delete()

    redirect_url = reverse('course', args=(course_pk,))
    return redirect(redirect_url)

@login_required
def task_download(request, pk):
    task = get_object_or_404(Task, pk=pk)
    redirect_url = reverse('course', args=(task.course.pk,))

    if not can(task.course, request.user, 'task.download'):
        messages.error(request, 'You are not allowed to download this task.')
        return redirect(redirect_url)

    filename = os.path.basename(task.file.name)
    response = HttpResponse(task.file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

@login_required
def submissions(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    redirect_url = reverse('course', args=(task.course.pk,))

    if not can(task.course, request.user, 'task.view'):
        messages.error(request, 'You are not allowed to view this task.')
        return redirect(redirect_url)

    view_all = 'all' in request.GET
    if view_all:
        if not can(task.course, request.user, 'submission.view'):
            messages.error(request, 'You are not allowed to view this task submissions.')
            return redirect(redirect_url)
        submissions = task.submissions.order_by('-created_at')
    else:
        submissions = task.submissions.filter(user=request.user).order_by('-created_at')

    return render(request, 'submissions.html', {'task': task, 'submissions': submissions, 'view_all': view_all})

@login_required
def leaderboard(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)

    if not can(task.course, request.user, 'task.view'):
        messages.error(request, 'You are not participating in this course.')
        return redirect(reverse('course', args=(task.course.pk,task_pk)))

    user_maxpoints = task.submissions.values('user') \
                                .annotate(max_point=Max('point')) \
                                .order_by('-max_point') \
                                .values('max_point')

    submissions = task.submissions.order_by('-point').filter(point__in=user_maxpoints).all()

    # Hack: otherwise will output multiple same user if got the same point on multiple submissions
    leaderboard_list, users = [], {}
    for s in submissions:
        if s.user.id not in users:
            users[s.user.id] = True
            leaderboard_list.append(s)

    return render(request, 'leaderboard.html', {'task': task, 'submissions': leaderboard_list})

@login_required
def submission_new(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    redirect_url = reverse('submissions', args=(course_pk,task_pk))

    if not can(task.course, request.user, 'task.submit'):
        messages.error(request, 'You are not allowed to submit this task.')
        return redirect(redirect_url)

    if not can(task.course, request.user, 'task.edit'):
        if not task.is_open:
            messages.error(request, 'Task is {}.'.format(task.get_status_display().lower()))
            return redirect(redirect_url)
        if not submission_is_allowed(task, request.user):
            messages.error(request, 'Daily submission limit exceeded.')
            return redirect(redirect_url)

    submission = Submission(task=task, user=request.user)
    form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
    if request.POST and form.is_valid():
        form.save()

        return redirect(redirect_url)

    return render(request, 'submission_new.html', {'form': form})

@login_required
def submission_download(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    redirect_url = reverse('submissions', args=(submission.task.course.pk,submission.task.pk))

    if not can(submission.task.course, request.user, 'submission.download', submission=submission):
        messages.error(request, 'You are not allowed to download this submission.')
        return redirect(redirect_url)

    filename = os.path.basename(submission.file.name)
    response = HttpResponse(submission.file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.cleaned_data['is_active'] = False
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            login(request, user)
            messages.info(request, 'Registration successful. Your account is currently pending approval.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})