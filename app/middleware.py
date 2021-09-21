import base64

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

AUTH_TEMPLATE = """ <html> <title>Authentication Required</title> <body> Access Denied. </body> </html> """


class SupportBasicAuthMiddleware(MiddlewareMixin):
    def _unauthed(self):
        response = HttpResponse(AUTH_TEMPLATE, content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self.get_response(request)
        else:
            authentication = request.META['HTTP_AUTHORIZATION']
            (auth_method, auth) = authentication.split(' ', 1)
            if 'basic' != auth_method.lower():
                return self._unauthed()
            auth = base64.b64decode(auth.strip()).decode('utf-8')
            username, password = auth.split(':', 1)

            user = authenticate(username=username, password=password)
            if user and user.is_active:
                login(request, user)
                return self.get_response(request)

            return self._unauthed()
