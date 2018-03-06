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
