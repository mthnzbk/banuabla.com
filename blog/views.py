from django.shortcuts import render, HttpResponseRedirect, Http404, HttpResponse, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from blog.models import Post


def home(request):
    paginator = Paginator(Post.objects.filter(publish__exact=True).order_by("-id"), 4)
    posts = paginator.page(1)
    return render(request, "blog/home.html", context={"posts": posts})

def page(request, page=1):
    if page == "" or int(page) == 1:
        return HttpResponseRedirect(reverse("blog"))

    paginator = Paginator(Post.objects.filter(publish__exact=True).order_by("-id"), 4)
    try:
        posts = paginator.page(int(page))
        return render(request, "blog/home.html", context={"posts": posts})

    except EmptyPage as err:
        print(err)
        raise Http404


def post_view(request, post_title):
    post = get_object_or_404(Post, title_url=post_title, publish=True)
    return render(request, "blog/post.html", context={"post": post})