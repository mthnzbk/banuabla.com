from django.shortcuts import render, Http404, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as djlogout, login as djlogin
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.mail import send_mail
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from banuabla.models import Order, Message, Image, User, Comments, BuyOrder
from banuabla.forms import (ContactForm, ProfileForm, RegisterForm, LoginForm, OrderAddForm, OrderMessageForm,
                            ForgotpasswdForm)
from banuabla.utils import image_clip, image_check, push_notify
import os
import requests
import json
import uuid


def home(request):
    contact_form = ContactForm()
    login_form = LoginForm()
    register_form = RegisterForm()
    forgot_form = ForgotpasswdForm()
    return render(request, "banuabla/home.html", context={"contact_form": contact_form, "login_form": login_form,
                                                          "register_form": register_form, "forgot_form": forgot_form})


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

    nocaptcha_query = requests.get(
        "https://www.google.com/recaptcha/api/siteverify?secret={}&response={}&remoteip={}".format(
            settings.RECAPTCHA_PRIVATE_KEY, request.POST.get("g-recaptcha-response"), request.META['REMOTE_ADDR']
        ))

    login_form = LoginForm(request.POST or None)

    if request.method == "POST":
        if login_form.is_valid() and nocaptcha_query.json()["success"]:

            user = authenticate(email=login_form.cleaned_data["email"], password=login_form.cleaned_data["password"])

            if user:
                djlogin(request, user)
                return HttpResponseRedirect(reverse("profile"))

            else:
                messages.error(request, "Girilen bilgiler doğru değil.")
                return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(request, "Girilen bilgiler doğru değil.")
            return HttpResponseRedirect(reverse("login"))

    return render(request, "banuabla/login.html", context={"login_form": login_form})


def logout(request):
    djlogout(request)
    return HttpResponseRedirect(reverse("home"))


def register(request):
    nocaptcha_query = requests.get(
        "https://www.google.com/recaptcha/api/siteverify?secret={}&response={}&remoteip={}".format(
            settings.RECAPTCHA_PRIVATE_KEY, request.POST.get("g-recaptcha-response"), request.META['REMOTE_ADDR']
        ))

    register_form = RegisterForm(request.POST or None)
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        if register_form.is_valid() and nocaptcha_query.json()["success"]:
            email = register_form.cleaned_data["user_email"]
            password = register_form.cleaned_data["user_password"]
            password2 = register_form.cleaned_data["user_password2"]

            if password != password2:
                messages.error(request, "Parolalar birbiriyle uyuşmuyor!")
                return HttpResponseRedirect(reverse("register"))

            try:
                user_create = User.objects.create_user(email, password)

            except IntegrityError as err:
                print(err)
                messages.error(request, "Bu E-Posta ile kayıtlı bir kullanıcı mevcut!")
                return HttpResponseRedirect(reverse("register"))

            user = authenticate(email=email, password=password)

            if "ref" in request.GET:
                ref = request.GET.get("ref")
                try:
                    ref_user = int(ref) - 1024
                    user_create.referanced_user_id = ref_user
                    user_create.save()

                except ValueError as err:
                    print(err)

            send_mail(subject="BanuAbla Hesap Aktivasyonu",
                      message="banuabla.com hesap aktivasyon bağlantınız.\n\nhttps://banuabla.com/activate/{}".format(
                          user.activate_code()),
                      from_email="cevapverme@banuabla.com", recipient_list=[user.email], fail_silently=True)

            if user:
                djlogin(request, user)
                return HttpResponseRedirect(reverse("profile"))

            else:
                return HttpResponseRedirect(reverse("home"))

        else:
            messages.error(request, "Hatalı e-posta adresi ya da parolanız 6 karakterden az!")

    return render(request, "banuabla/register.html", context={"register_form": register_form})


def forgotpasswd(request, code=None):
    if code:
        try:
            user = User.objects.get(forgotcode=code)
            djlogin(request, user)
            user.forgotcode = uuid.uuid4()
            user.save()
            messages.warning(request, "Yeni parolanızı girmeyi unutmayın!")
            return HttpResponseRedirect(reverse("profile"))

        except ObjectDoesNotExist as err:
            return HttpResponseRedirect(reverse("home"))

    forgot_form = ForgotpasswdForm(request.POST or None)

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        if forgot_form.is_valid():
            email = forgot_form.cleaned_data["forgot_email"]

            try:
                user = User.objects.get(email=email)

                send_mail(subject="BanuAbla Hesap Parolası Sıfırla",
                          message="banuabla.com hesap sıfırlama bağlantınız.\n\nhttps://banuabla.com/forgotpasswd/{}".format(
                              user.activate_code()),
                          from_email="cevapverme@banuabla.com", recipient_list=[user.email], fail_silently=True)
                messages.success(request, "Parola sıfırlama bağlantısı e-posta adresinize gönderilmiştir.")

            except ObjectDoesNotExist as err:
                messages.error(request, "Bu e-posta sistemde kayıtlı değil!")
                return HttpResponseRedirect(reverse("forgotpasswd"))

    return render(request, "banuabla/forgotpasswd.html", context={"forgot_form": forgot_form})


@login_required
def profile(request):
    profile_form = ProfileForm(request.POST or None)
    user = User.objects.get(email=request.user.email)
    profile_form.initial = {
        "last_name": user.last_name,
        "first_name": user.first_name,
        "birth": user.birth,
        "gender": user.gender,
        "about": user.about
    }

    if request.method == "POST":
        if request.FILES.get("user_photo"):
            photo = request.FILES['user_photo']
            path = os.path.join(settings.MEDIA_ROOT, "profil")

            fs = FileSystemStorage(location=path)
            if not image_check(photo.file.read()):
                messages.error(request, "Yüklediğiniz bir fotoğraf değil.")

            else:
                filename = fs.save(photo.name, photo)
                image_clip(os.path.join(path, filename))
                user.user_photo = os.path.join("profil", filename)
                user.save()

            return HttpResponseRedirect(reverse("profile"))

        if profile_form.is_valid():
            user.first_name = profile_form.cleaned_data["first_name"]
            user.last_name = profile_form.cleaned_data["last_name"]
            user.birth = profile_form.cleaned_data["birth"]
            user.gender = profile_form.cleaned_data["gender"]
            user.about = profile_form.cleaned_data["about"]

            if profile_form.cleaned_data["password"] == profile_form.cleaned_data["password2"] and \
                    profile_form.cleaned_data["password"] != "":
                user.set_password(profile_form.cleaned_data["password"])

            elif profile_form.cleaned_data["password"] != "":
                messages.warning(request, "Veriler uyuşmadığı için parola değişmedi.")

            user.save()

            return HttpResponseRedirect(reverse("profile"))

        else:
            messages.error(request, "Geçersiz bilgi girdiniz.")

    return render(request, "banuabla/profile.html", context={"profile_form": profile_form})


def panel(request, user_id=None):
    if not request.user.is_staff:
        raise Http404

    if user_id:
        orders = Order.objects.filter(user__id=user_id).order_by("-id")

    else:
        orders = Order.objects.all().order_by("-id")

    return render(request, "banuabla/panel.html", context={"orders": orders})


@login_required
def order(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse("panel"))

    orders = Order.objects.filter(user__email=request.user.email).order_by("-id")
    return render(request, "banuabla/order.html", context={"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_staff and order.user != request.user:
        return HttpResponseRedirect(reverse("order"))

    _messages = order.message_set.all()
    fal_photos = order.image_set.all()
    message_form = OrderMessageForm(request.POST or None)

    if request.method == "POST":
        if message_form.is_valid():
            if request.FILES:
                sound = request.FILES.get('sound', None)
                path = os.path.join(settings.MEDIA_ROOT, "fal-yorumu")

                fs = FileSystemStorage(location=path)
                if sound:
                    filename = fs.save(sound.name, sound)
                    order.fal_yorumu = os.path.join("fal-yorumu", filename)
                    order.save()

            if message_form.cleaned_data["message"] != "":
                message = Message.objects.create(user=request.user, order=order)
                message.content = message_form.cleaned_data["message"]
                message.save()

                if request.user.is_staff:
                    send_mail("{} adlı kişiden mesaj var!".format(request.user.full_name()),
                              "{} adlı kişi siparişinize yanıt verdi. Siparişe ulaşmak için tıklayın: \
                              https://banuabla.com/order/{}".format(request.user.full_name(), order.id),
                              "cevapverme@banuabla.com", [order.user.email], fail_silently=True)

                    push_notify(order.user.email, "Siparişinize yanıt geldi!",
                                "SP{} nolu siparişinize yanıt geldi! Siparişe ulaşmak için tıklayın".format(order.id),
                                "https://banuabla.com/order/{}".format(order.id))

                else:
                    send_mail("{} adlı kişiden mesaj var!".format(request.user.full_name()),
                              "{} adlı kişi siparişine mesaj yazdı. Siparişe ulaşmak için tıklayın: \
                              https://banuabla.com/order/{}".format(request.user.full_name(), order.id),
                              "cevapverme@banuabla.com", ["ozbekbanu@hotmail.com"], fail_silently=True)

                    push_notify("ozbekbanu@hotmail.com", "{} siparişine mesaj yazdı.".format(request.user.full_name()),
                                "SP{} nolu siparişe {} mesaj yazdı.".format(order.id, request.user.full_name()),
                                "https://banuabla.com/order/{}".format(order.id))

            if "fal_teslim" in request.POST:
                if order.fal_yorumu:
                    order.order_status = True
                    order.save()

                    send_mail("Tebrikler! Siparişiniz tamamlandı.",
                              "Tebrikler! Banu Abla siparişinizi tamamladı. Siparişinize ulaşmak için tıklayın: \
                              https://banuabla.com/order/{}".format(order.id),
                              "cevapverme@banuabla.com", [order.user.email], fail_silently=True)

                    push_notify(order.user.email, "Tebrikler! Siparişiniz tamamlandı.",
                                "SP{} nolu siparişiniz tamamlandı. Falınızı dinlemek için tıklayın.".format(order.id),
                                "https://banuabla.com/order/{}".format(order.id))

                else:
                    messages.warning(request, "Ses kaydınızı yollamadan siparişi tamamlayamazsın!")

            return HttpResponseRedirect(reverse("order_detail", args=(order_id,)))

    return render(request, "banuabla/order_detail.html", context={"order": order, "order_messages": _messages,
                                                                  "fal_photos": fal_photos, "message_form": message_form})


@login_required
def order_add(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse("panel"))

    if request.user.fal_credit == 0 and not request.user.is_staff:
        return HttpResponseRedirect(reverse("buy"))

    if request.method == "POST":
        add_form = OrderAddForm(request.POST)
        if add_form.is_valid():
            if request.FILES:
                fal1 = request.FILES.get('fal1', None)
                fal2 = request.FILES.get('fal2', None)
                fal3 = request.FILES.get('fal3', None)
                fal4 = request.FILES.get('fal4', None)
                fals = [fal1, fal2, fal3, fal4]
                path = os.path.join(settings.MEDIA_ROOT, "photo")

                fs = FileSystemStorage(location=path)
                for fal in fals:
                    if fal and not image_check(fal.file.read()):
                        messages.error(request, "Yüklediğiniz bir fotoğraf değil.")
                        return HttpResponseRedirect(reverse("order_add"))

                    elif not fal:
                        continue

                order = Order.objects.create(user=request.user)

                for fal in fals:
                    if fal:
                        image = Image.objects.create(order=order)
                        filename = fs.save(fal.name, fal)
                        image.image = os.path.join("photo", filename)
                        image.save()

                if add_form.cleaned_data["message"]:
                    message = Message.objects.create(user=request.user, order=order)
                    message.content = add_form.cleaned_data["message"]
                    message.save()

            else:
                messages.error(request, "Hiç fotoğraf seçmediniz. Lütfen fotoğrafları eksiksiz seçiniz!")
                return HttpResponseRedirect(reverse("order_add"))

            user = User.objects.get(email=request.user.email)
            user.fal_credit -= 1
            user.fal_point += 1
            user.save()
            if user.referanced_user:
                ref_user = User.objects.get(email=user.referanced_user)
                ref_user.fal_point += 1
                ref_user.save()

            send_mail("{} adlı kişiden sipariş var!".format(user.full_name()),
                      "{} adlı kişi kahve falı siparişi verdi. Siparişe ulaşmak için tıklayın: \
                      https://banuabla.com/order/{}".format(user.full_name(), order.id),
                      "cevapverme@banuabla.com", ["ozbekbanu@hotmail.com"], fail_silently=True)

            push_notify("ozbekbanu@hotmail.com",
                        "Tebrikler! Yeni bir siparişin var!",
                        "Tebrikler! {} adlı kişiden yeni bir siparişin var.".format(order.user.full_name()),
                        "https://banuabla.com/order/{}".format(order.id))

            return HttpResponseRedirect(reverse("order_detail", args=(order.id,)))

    order = Order.objects.filter(user__email=request.user.email)
    return render(request, "banuabla/order_add.html", context={"orders": order})


def contact(request):
    nocaptcha_query = requests.get("https://www.google.com/recaptcha/api/siteverify?secret={}&response={}&remoteip={}".format(
        settings.RECAPTCHA_PRIVATE_KEY, request.POST.get("g-recaptcha-response"), request.META['REMOTE_ADDR']
    ))

    contact_form = ContactForm(request.POST or None)
    if request.method == "POST":
        if contact_form.is_valid() and nocaptcha_query.json()["success"]:
            message = "<h1>{}</h1><h5>{}</h5><p>{}</p>".format(contact_form.cleaned_data["full_name"],
                                                               contact_form.cleaned_data["guest_email"],
                                                               contact_form.cleaned_data["message"])
            send_mail(subject=contact_form.cleaned_data["subject"],
                      message=message,
                      from_email="cevapverme@banuabla.com",
                      recipient_list=["banuabla@banuabla.com"],
                      fail_silently=True, html_message=message)
            messages.success(request, "Mesajın bize ulaştı.")
            return HttpResponseRedirect(reverse("home")+"#contact")

        else:
            messages.error(request, "Bir hata yaptın sanırım.")
            return HttpResponseRedirect(reverse("home")+"#contact")

    return HttpResponseRedirect(reverse("home"))


@login_required
def buy(request):
    return render(request, "banuabla/buy.html")


@login_required
@csrf_exempt
def buy_done(request):
    if request.method == "POST" and request.POST.get("buy"):
        sp = BuyOrder.objects.create(user=request.user, shopping_cart=request.POST.get("buy"))
        js = {
            "SP": sp.sp_no(),
            "price": sp.price(),
            "success": True,

        }

        send_mail(subject="Banu Abla, {} adlı kişi kredi siparişi verdi!".format(request.user.full_name() or request.user),
                  message="""{} adlı kişi {} koduyla fal kredisi siparişi verdi.
                   Ödeme yapar diye takibini yapmayı unutma!""".format(request.user.full_name() or request.user,
                                                                      sp.sp_no()),
                  from_email="cevapverme@banuabla.com", recipient_list=["banuabla@banuabla.com"], fail_silently=True)

        return JsonResponse(js, safe=False)

    else:
        return HttpResponseRedirect(reverse("buy"))


def activate(request, activate_code=None):
    if not activate_code:
        send_mail(subject="BanuAbla Hesap Aktivasyonu",
                  message="banuabla.com hesap aktivasyon bağlantınız.\n\nhttps://banuabla.com/activate/{}".format(
                      request.user.activate_code()),
                  from_email="cevapverme@banuabla.com", recipient_list=[request.user.email], fail_silently=True)

    else:
        try:
            user = User.objects.get(forgotcode=activate_code)
            user.is_verify = True
            user.forgotcode = uuid.uuid4()
            user.save()
            return HttpResponseRedirect(reverse("profile"))

        except ObjectDoesNotExist as err:
            return HttpResponseRedirect(reverse("home"))

    return HttpResponseRedirect(reverse("home"))


def comments(request):
    jsl = []
    j = serializers.serialize("json", Comments.objects.all())
    for i in json.loads(j):
        jsl.append(i["fields"])
    return HttpResponse(json.dumps(jsl), content_type="application/json")


def gizlilik(request):
    return render(request, "kullanim-gizlilik.html")


def sss(request):
    return render(request, "sss.html")


def handler404(request):
    return render(request, "404.html")


def handler500(request):
    return render(request, "500.html")


def onesignal(request):
    return HttpResponse("importScripts('https://cdn.onesignal.com/sdks/OneSignalSDKWorker.js');", content_type="text/javascript")


def manifest(request):
    return HttpResponse("""{
  "gcm_sender_id": "482941778795",
  "gcm_sender_id_comment": "Do not change the GCM Sender ID"
}""", content_type="text/json")
