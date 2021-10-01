from django.conf import settings
from django.contrib.auth.models import User

from app.models import Course, Participation, Submission


def has_perm(course: Course, user: User, action: str, participation: Participation = None, submission: Submission = None):
    """Check permission based on course, user and action. List of action can be found under ROLES in `settings.py`
    """
    if submission and submission.user == user:
        return True
    if not participation:
        participation = Participation.objects.filter(user=user, course=course).first()
    if not participation:
        return False
    return participation.role in settings.ROLES[action]
