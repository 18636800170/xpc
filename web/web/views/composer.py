from django.http import JsonResponse
from django.shortcuts import render
from web.helprs.composer import get_posts_by_cid
from web.models.composer import Composer


def oneuser(request, cid):
    composer = Composer.objects.get(cid=cid)
    composer.posts = get_posts_by_cid(composer.cid, 2)
    return render(request, "oneuser.html", locals())


def homepage(request, cid):
    composer = Composer.objects.get(cid=cid)
    composer.posts = get_posts_by_cid(cid)
    composer.rest_posts = composer.posts[1:]
    return render(request, "homepage.html", locals())


def register(request):
    return render(request, "register.html")


def do_register(request):
    nickname = request.POST.get("nickname")
    phone = request.POST.get("phoone")
    code = request.POST.get("code")
    password = request.POST.get("password")
    prefix_code = request.POST.get("prefix_code")
    callback = request.POST.get("callback")

    if Composer.objects.filter(phone=phone).exists():
        data = {
            "status": -1025,
            "msg": "该手机号已经注册过",
        }
        return JsonResponse(data)
    composer = Composer()
    composer.name=nickname
    composer.cid = composer.phone = phone
    composer.password = password
    composer.avatar=""
    composer.verified=0
    composer.banner=""
    composer.save()
    return JsonResponse({})