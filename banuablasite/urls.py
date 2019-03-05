from django.conf.urls import url, handler404, handler500, include
from django.urls import path
from django.contrib import admin
from banuabla import views
from django.conf.urls.static import static
from django.conf import settings


handler404 = views.handler404
handler500 = views.handler500


urlpatterns = [
    path("adminx/", admin.site.urls),
    path("kullanim-ve-gizlilik/", views.gizlilik, name="gizlilik"),
    path("sss/", views.sss, name="sss"),
    path("activate/", views.activate, name="activate"),
    path("activate/<uuid:activate_code>", views.activate, name="activate"),
    path("summernote/", include('django_summernote.urls')),
    path("blog/", include("blog.urls")),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("forgotpasswd/", views.forgotpasswd, name="forgotpasswd"),
    path("forgotpasswd/<uuid:code>/", views.forgotpasswd, name="forgotpasswd_uuid"),
    path("panel/", views.panel, name="panel"),
    path("panel/<int:user_id>", views.panel, name="panel_user"),
    path("profile/", views.profile, name="profile"),
    path("order/", views.order, name="order"),
    path("order/<int:order_id>", views.order_detail, name="order_detail"),
    path("order/add/", views.order_add, name="order_add"),
    path("buy/", views.buy, name="buy"),
    path("buy/done", views.buy_done, name="buy_done"),
    path("comments/", views.comments, name="comments"),
    path("contact/", views.contact, name="contact"),
    path("OneSignalSDKWorker.js", views.onesignal),
    path("OneSignalSDKUpdaterWorker.js", views.onesignal),
    path("manifest.json", views.manifest),
    path("", views.home, name="home"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)