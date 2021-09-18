from django import template
from ..utils.permission import can

register = template.Library()

register.simple_tag(can)