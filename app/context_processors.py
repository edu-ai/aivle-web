from .funcs import get_announcements

def announcements(request):
    return { 'announcements': get_announcements() }