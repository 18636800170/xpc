from django.http import HttpResponseRedirect
from web.models.composer import Composer

need_login = ["/"]


class AuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in need_login:
            cid = request.COOKIE.get("cid")
            if not cid:
                return HttpResponseRedirect("/login/")

            request.composer = Composer.get(cid=cid)
        response = self.get_response(request)

        return response
