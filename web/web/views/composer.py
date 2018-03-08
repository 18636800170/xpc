import random
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from web.helprs.code import gen_code, verify_code
from web.helprs.composer import get_posts_by_cid, md5_pwd
from web.helprs.task import send_sms_code
from web.models.code import Code
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
    phone = request.POST.get("phone")
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

    if not verify_code(phone, code):
        return JsonResponse({
            "status": -1,
            "msg": "手机验证失败",
        })

    composer = Composer()
    composer.name = nickname
    composer.cid = composer.phone = phone
    composer.password = md5_pwd(phone, password)
    composer.avatar = ""
    composer.verified = 0
    composer.banner = ""
    composer.save()

    return JsonResponse({
        "status": 0,
        "data": {
            "callback": "/",
        }
    })


def login(request):
    return render(request, "login.html")


def do_login(request):
    phone = request.POST.get("phone")
    password = request.POST.get("password")
    composer = Composer.get_by_phone(phone)
    if not composer or composer.password != md5_pwd(phone, password):
        return JsonResponse({
            "status": -1,
            "msg": "用户名或密码错误"
        })

    response = JsonResponse({
        "status": 0,
        "data": {
            "callback": "/",
        }
    })
    response.set_cookie("cid", composer.cid)
    response.set_cookie("token", md5_pwd(composer.cid, settings.SECRET_KEY))
    return response


def send_code(request):
    prefix_code = request.POST.get("prefix_code")
    phone = request.POST.get("phone")
    composer = Composer.get_by_phone(phone)
    if composer:
        return JsonResponse({
            "status": -1025,
            "msg": "该手机号已经注册过",
        })

    code = Code()
    code.phone = phone
    code.code = gen_code()
    code.ip = request.META["REMOTE_ADDR"]
    code.created_at = datetime.now()
    code.save()
    send_sms_code.delay(phone, code.code)
    return JsonResponse({
        "status": 0,
        "msg": "ok",
        "data": {
            "phone": phone,
            "prefix_code": prefix_code,
        },
    })


def logout(request):
    response = HttpResponseRedirect("/")
    response.delete_cookie("cid")
    return response


def find_password(request):
    return render(request, "find_password.html")


def check_send(request):
    prefix_code = request.POST.get("prefix_code")
    phone = request.POST.get("phone")
    composer = Composer.get_by_phone(phone)
    if not composer:
        return JsonResponse({
            "status": -1025,
            "msg": "该手机号未注册过",
        })

    code = Code()
    code.phone = phone
    code.code = gen_code()
    code.ip = request.META["REMOTE_ADDR"]
    code.created_at = datetime.now()
    code.save()
    send_sms_code.delay(phone, code.code)
    return JsonResponse({
        "status": 0,
        "msg": "ok",
    })


def mobile_check(request):
    phone = request.POST.get("phone")
    code = request.POST.get("code")
    prefix_code = request.POST.get("prefix_code")
    composer = Composer.get_by_phone(phone)
    if not composer:
        return JsonResponse({
            "status": -1025,
            "msg": "该手机号未注册过",
        })
    if not verify_code(phone, code):
        return JsonResponse({
            "status": -1,
            "msg": "用户名或密码错误"
        })
    response = JsonResponse({
        "status": 0,
        "msg": "ok",
    })
    ls = str(random.randint(100000, 999999))
    response.set_cookie("laravel_session", ls, expires=datetime.now() + timedelta(minutes=5))
    response.set_cookie("phone",phone,expires=datetime.now() + timedelta(minutes=5))
    cache.set(phone,ls,timeout=60*5)
    return response


def reset_pwd(request):
    phone=request.COOKIES.get("phone")
    password=request.POST.get("password")
    reset_passsword=request.POST.get("reset_password")
    if password !=reset_passsword:
        return JsonResponse({
            "status":-10005,
            "msg":"两次输入的密码不正确",
        })
    if request.COOKIES.get("laravel_session") != cache.get(phone):
        return JsonResponse({
            "status": -1,
            "msg": "param error",
        })
    composer=Composer.get_by_phone(phone)
    composer.password=md5_pwd(phone,password)
    composer.save()
    return JsonResponse({
        "status":0,
        "msg":"ok",
        "data": {
            "callback": "/login/",
        }
    })
