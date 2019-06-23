from django import template
from ..funcs import submission_is_allowed

register = template.Library()

register.simple_tag(submission_is_allowed)