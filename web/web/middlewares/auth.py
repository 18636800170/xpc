from django.conf import settings
from django.http import HttpResponseRedirect
from web.helprs.composer import md5_pwd
from web.models.composer import Composer

need_login = ["/"]


class AuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in need_login:
            cid = request.COOKIES.get("cid")
            token=request.COOKIES.get("token")
            if not cid or md5_pwd(cid,settings.SECRET_KEY)!=token:
                return HttpResponseRedirect("/login/")

            request.composer = Composer.get(cid=cid)
        response = self.get_response(request)

        return response
