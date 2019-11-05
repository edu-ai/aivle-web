from django import template
from django.utils.safestring import mark_safe

register = template.Library()

AUTOLINKS = {
    'AgentInstallError': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#agentinstallerror',
    'AgentNotFound': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#agentnotfound',
    'TimeoutException': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#timeoutexception',
    'MalformedOutputError': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#malformedoutputerror',
    'RunnerError': 'https://github.com/cs4246/meta/wiki/Frequently-Asked-Questions#runnererror'
}

def wrap_link(text, url):
    return '<a href="{}" target="_blank">{}</a>'.format(url, text)

@register.filter(is_safe=True)
def autolink(value):
    for k, v in AUTOLINKS.items():
        try:
            value = value.replace(k, wrap_link(k, v))
        except:
            pass
    return mark_safe(value)