from django import template
from django.utils.safestring import mark_safe

register = template.Library()

AUTOLINKS = [
    {
        'word': 'AgentInstallError',
        'link': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#agentinstallerror'
    },
    {
        'word': 'AgentNotFound',
        'link': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#agentnotfound'
    },
    {
        'word': 'TimeoutException',
        'link': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#timeoutexception'
    },
    {
        'word': 'MalformedOutputError',
        'link': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#malformedoutputerror'
    },
    {
        'word': 'RunnerError',
        'link': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#runnererror'
    }
]

@register.filter(is_safe=True)
def autolink(value):
    for target in AUTOLINKS:
        try:
            value = value.replace(target['word'], '<a href="{}" target="_blank">{}</a>'.format(target['link'], target['word']))
        except:
            pass
    return mark_safe(value)