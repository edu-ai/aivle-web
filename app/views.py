from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Max

from .models import Course, Task, Submission, Participation
from .forms import TaskForm, SubmissionForm, CourseForm
from .funcs import can, submission_is_allowed, course_participations, course_participation


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

    form = TaskForm(request.POST or None, instance=task)
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
def submissions(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    redirect_url = reverse('course', args=(task.course.pk,))

    if not can(task.course, request.user, 'task.view'):
        messages.error(request, 'You are not allowed to view this task submissions.')
        return redirect(redirect_url)

    submissions = task.submissions.filter(user=request.user)

    return render(request, 'submissions.html', {'task': task, 'submissions': submissions})

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

    submissions = task.submissions.order_by('-point').filter(point__in=user_maxpoints)

    return render(request, 'leaderboard.html', {'task': task, 'submissions': submissions})

@login_required
def submission_new(request, course_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    redirect_url = reverse('submissions', args=(course_pk,task_pk))

    if not can(task.course, request.user, 'task.submit'):
        messages.error(request, 'You are not allowed to submit this task.')
        return redirect(redirect_url)

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