from django import template
from ..funcs import can

register = template.Library()

register.simple_tag(can)