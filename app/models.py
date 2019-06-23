from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import os


def submission_path(instance, filename):
    return 'submissions/course_{}/task_{}/user_{}/{}_{}'.format(
        instance.task.course.id, instance.task.id, instance.user.id, timezone.now().timestamp(), filename
    )


class Course(models.Model):
    class Meta:
        unique_together = (('code', 'academic_year', 'semester'),)

    code = models.CharField(max_length=6)
    academic_year = models.CharField(max_length=30)
    semester = models.PositiveSmallIntegerField()
    participants = models.ManyToManyField(
        User,
        through='Participation',
        through_fields=('course', 'user'),
    )

    def __str__(self):
        return "{} - {} Semester {}".format(self.code, self.academic_year, self.semester)

    def __eq__(self, other):
        if not isinstance(other, Course):
            return False
        return self.code == other.code and self.academic_year == other.academic_year and self.semester == other.semester

    def __hash__(self):
        return hash((self.code, self.academic_year, self.semester))


class Participation(models.Model):
    ROLE_ADMIN = 'ADM'
    ROLE_GUEST = 'GUE'
    ROLE_STUDENT = 'STU'
    ROLE_LECTURER = 'LEC'
    ROLE_TEACHING_ASSISTANT = 'TA'
    ROLES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_GUEST, 'Guest'),
        (ROLE_STUDENT, 'Student'),
        (ROLE_LECTURER, 'Lecturer'),
        (ROLE_TEACHING_ASSISTANT, 'Teaching Assistant')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=3,
        choices=ROLES,
        default=ROLE_STUDENT,
    )

    def __str__(self):
        return "{} ({}) - {} AY{} Sem{}".format(self.user.username, self.role, self.course.code, self.course.academic_year, self.course.semester)


class Task(models.Model):
    DEFAULT_RUNTIME_LIMIT = timedelta(seconds=10)
    DEFAULT_MAX_UPLOAD_SIZE = 5 * 1024 # KB
    DEFAULT_DAILY_SUBMISSIONS_LIMIT = 3

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    daily_submission_limit = models.PositiveSmallIntegerField(default=DEFAULT_DAILY_SUBMISSIONS_LIMIT)
    runtime_limit = models.DurationField(default=DEFAULT_RUNTIME_LIMIT)
    max_upload_size = models.IntegerField(default=DEFAULT_MAX_UPLOAD_SIZE)

    opened_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    leaderboard = models.BooleanField(default=False)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subtasks', null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tasks')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.name)

    @property
    def is_open(self):
        if self.opened_at and self.opened_at > timezone.now():
            return False
        if self.is_dead:
            return False
        return True

    @property
    def is_dead(self):
        return self.closed_at and self.closed_at < timezone.now()

    def get_status_display(self):
        if self.is_dead:
            return "Overdue"
        return "Open" if self.is_open else "Scheduled"

    def __str__(self):
        return "{} - {} AY{} Sem{}".format(self.name, self.course.code, self.course.academic_year, self.course.semester)
    

class Submission(models.Model):
    STATUS_QUEUED = 'Q'
    STATUS_RUNNING = 'R'
    STATUS_ERROR = 'E'
    STATUS_DONE = 'D'
    STATUSES = [
        (STATUS_QUEUED, 'Queued'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_ERROR, 'Error'),
        (STATUS_DONE, 'Done')
    ]

    VERDICT_NONE = 'NA'
    VERDICT_ACCEPTED = 'AC'
    VERDICT_WRONG_ANSWER = 'WA'
    VERDICT_TIME_LIMIT_EXCEEDED = 'TLE'
    VERDICTS = [
        (VERDICT_NONE, 'None'),
        (VERDICT_ACCEPTED, 'Accepted'),
        (VERDICT_WRONG_ANSWER, 'Wrong Answer'),
        (VERDICT_TIME_LIMIT_EXCEEDED, 'Time Limit Exceeded'),
    ]

    RUNNER_PYTHON = 'PY'
    RUNNER_DOCKER = 'DO'
    RUNNERS = [
        (RUNNER_PYTHON, 'Python'),
        (RUNNER_DOCKER, 'Docker')
    ]


    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=submission_path, blank=True, null=True)

    runner = models.CharField(
        max_length=2,
        choices=RUNNERS,
        default=RUNNER_PYTHON,
    )
    metadata = models.TextField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')

    status = models.CharField(
        max_length=1,
        choices=STATUSES,
        default=STATUS_QUEUED,
    )
    verdict = models.CharField(
        max_length=3,
        choices=VERDICTS,
        default=VERDICT_NONE,
    )
    point = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else None

    def __str__(self):
        return "{}:{} - {} - {} AY{} Sem{}".format(self.user, self.pk, self.task.name, 
            self.task.course.code, self.task.course.academic_year, self.task.course.semester)