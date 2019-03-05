from django.conf.urls import url
from blog import views



urlpatterns = [
    url(r'^page/(?P<page>\d*)$', views.page, name="page_view"),
    url(r'^post/(?P<post_title>[\w-]+)\.html$', views.post_view, name="post_view"),
    url(r'^$', views.home, name="blog"),
]