from .models import Participation, Course
from .forms import CourseForm
from django.conf import settings
from django.utils import timezone
from collections import namedtuple
from cachetools import cached, TTLCache


CourseParticipation = namedtuple('CourseParticipation', ['course', 'participation', 'added', 'joined', 'form'], defaults=(None,) * 5)


def can(course, user, action, participation=None, submission=None):
    if submission and submission.user == user:
        return True
    if not participation:
        participation = Participation.objects.get(user=user, course=course)
    return participation and participation.role in settings.ROLES[action]


def submission_is_allowed(task, user):
    user_today_submissions = task.submissions.filter(user=user).filter(created_at__gt=timezone.now().date())
    return task.daily_submission_limit and user_today_submissions.count() < task.daily_submission_limit


def serialize_submission(s):
    return {
        'id': s.id, 
        'runner': s.runner, 
        'metadata': s.metadata, 
        'path': s.file.path if s.file else None,
        'status': s.status,
        'verdict': s.verdict,
        'point': s.point,
        'notes': s.notes,
    }


# Cache result for 1 hour
@cached(cache=TTLCache(maxsize=1024, ttl=60*60))
def get_course_roles_from_luminus(user):
    # DUMMY, replace with API call to luminus
    roles = [Participation.ROLE_LECTURER, Participation.ROLE_STUDENT, Participation.ROLE_GUEST]
    course_roles = []
    for i, code in enumerate(['CS4246', 'CS0001', 'CS0002', 'CS0003', 'CS0004']):
        course = Course(code=code, academic_year="2019/2020", semester=1)
        role = roles[i % len(roles)]
        course_roles.append((course, role))
    return course_roles


def course_participations(user, with_form=False, hidden_form=True):
    availables = Course.objects.all()
    participated = Course.objects.filter(participants__in=[user]).all()

    cp_participated = [CourseParticipation(c, Participation.objects.get(user=user, course=c), True, True) for c in participated]

    rests = [course for course in availables if course not in participated]
    cp_rests = []

    for course, role in get_course_roles_from_luminus(user):
        participation = Participation(user=user, course=course, role=role)

        if course in participated:
            continue

        added_courses = [c for c in rests if c == course]
        added = len(added_courses) > 0
        if added:
            course = added_courses[0]

        form = None
        if not added and with_form:
            form = CourseForm(None, instance=course, hidden=hidden_form)

        cp_rests.append(CourseParticipation(course, participation, added, False, form))

    return cp_participated + cp_rests


def course_participation(user, course):
    cps = course_participations(user)
    cp = next(filter(lambda cp: cp.course == course,  cps))
    return cp