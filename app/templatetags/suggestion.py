from django import template
from django.utils.safestring import mark_safe
import re

from .autolink import AUTOLINKS, wrap_link

register = template.Library()

SUGGESTIONS = {
    r"FileNotFoundError.+\.pt": 
        'You have to zip everything inside the agent template, including the \
        <a href="https://packaging.python.org/guides/using-manifest-in/" target="_blank">MANIFEST.in</a>.\
        Also, please make sure that you have included the model / checkpoint *.pt file in its appropriate location inside the zip file.\
        If you haven\'t already, use the absolute path relative to the script file whenever possible for consistency.',
    r"TypeError: can't convert CUDA tensor to numpy": 
        'Use <a href="https://pytorch.org/docs/stable/tensors.html#torch.Tensor.cpu" target="_blank">Tensor.cpu()</a>\
        to copy the tensor to host memory first before converting to Numpy.',
    r"fast-downward.py: not found|fast-downward.py: Permission denied": 
        'Please make sure to follow the submission guideline regarding the path to the Fast Downward.\
        For the Mini Project sample agent, the path is given in the <b>initialize</b> function.',
    r"pyenv: command not found|SuiteInstallError|RunnerInstallError": 
        "The runner has failed unexpectedly. Please contact the teaching staff to get the submission regraded.",
    r'{"error": {"type": "RunnerError", "args": \[""\]}}':
        "Please make sure that you are aware of our system <a href='https://github.com/cs4246/meta/wiki/Known-Issues' target='_blank'>known issues</a>.",
    r'deterministic.+1\.|deterministic.+2\.|deterministic.+3\.|deterministic.+4\.|deterministic.+5\.|deterministic.+6\.|deterministic.+7\.': 
        "Please check that your loss function is correct. Make sure that you incorporate `dones` as it is required to correctly compute\
        the Q function for the terminal states, since Q(s,a) = R(s,a) for a terminal state s and any arbitrary action a.\
        Other reason might be because the proper gradient computation can't be computed due to the lack of continuity in the comptational graph.\
        In that case, you might want to make sure that you operate directly in the PyTorch tensor, without copying or converting the tensor.\
        Also, check the other function implementations for error as well."
}

EXTRA = "<hr><b>Before asking questions</b>, please make sure that you have:\
<ol>\
    <li>Tried hard to figure out the source of the error</li>\
    <li>Followed the suggestion given by aiVLE</li>\
    <li>Read the clarifications thread in Luminus carefully</li>\
    <li>Search the Luminus forum for a potential fix</li>\
</ol>\
Please present the <i>details</i> of the error, a <i>summary</i> on what you have tried, and your <i>conjecture</i> regarding the problem.\
"

@register.filter(is_safe=True)
def suggestion(value):
    if value is None:
        return None
    for k, v in SUGGESTIONS.items():
        matches = re.findall(k, value)
        if matches:
            return mark_safe(v + EXTRA)
    for k, v in AUTOLINKS.items():
        if k in value:
            return mark_safe('Please refer to {}.'.format(wrap_link(k, v)) + EXTRA)
    if re.findall(r"Error|error", value):
        return mark_safe('Please read the error message carefully and fix accordingly. Also, make sure that you have tested your agent locally with the original ``test`` function given in the agent template.' + EXTRA)
    return None