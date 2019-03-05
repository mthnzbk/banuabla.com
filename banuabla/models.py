from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
import time


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Süper kullanıcı için is_staff=True yapmalısınız.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Süper kullanıcı için is_superuser=True yapmalısınız.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    cinsiyet = (
        (None, "Cinsiyetinizi Seçiniz"),
        ("K", "Kadın"),
        ("E", "Erkek")
    )
    referanced_user = models.ForeignKey("User", verbose_name="Refansı", null=True, blank=True, default="", on_delete=models.CASCADE)
    user_photo = models.ImageField(verbose_name="Profil Fotoğrafı", upload_to="profil/", null=True, blank=True)
    fal_credit = models.IntegerField(verbose_name="Fal Baktırma Hakkı", default=0)
    fal_point = models.IntegerField(verbose_name="Fal Puanı", default=0)
    gender = models.CharField(max_length=1, verbose_name="Cinsiyeti", null=True, default=None, blank=True, choices=cinsiyet)
    birth = models.IntegerField(default=1900, verbose_name="Doğum Yılı")
    about = models.CharField(max_length=500, verbose_name="Hakkında", null=True, blank=True)
    login_ip = models.GenericIPAddressField(verbose_name="Son Giriş IP", null=True, blank=True)
    is_verify = models.BooleanField(default=False, verbose_name="Doğrulanmış")
    forgotcode = models.UUIDField(default=uuid.uuid4, editable=False)

    username = None
    email = models.EmailField(verbose_name="E-Posta", unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.fal_point >= 20:
            self.fal_point -= 20
            self.fal_credit += 1
        super().save(*args, **kwargs)

    def activate_code(self):
        return self.forgotcode

    def referanced_link(self):
        return self.id + 1024

    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Kullanıcılar"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Siparişi Veren")
    fal_yorumu = models.FileField(upload_to="fal-yorumu", verbose_name="Fal Yorumu", null=True)
    order_status = models.BooleanField(verbose_name="Sipariş Tamamlandı", default=False)
    order_date = models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name="Sipariş Zamanı")

    def tahmini(self):
        sira = Order.objects.filter(order_status__exact=False, order_date__lt=self.order_date).count()

        if sira + time.localtime().tm_hour > 23:
            return "Ertesi Gün İçerisinde"
        else:
            return "Gün İçerisinde"

    def started(self):
        orders = Order.objects.filter(order_status__exact=False, order_date__lt=self.order_date)
        if not orders.count():
            return "Sıra Sizde"
        else:
            return "Sırada {} Fal Var".format(orders.count())

    def status(self):
        if self.order_status:
            return "Teslim Edildi"

        else:
            return "Teslim Edilmedi"

    def clean_fal_yorumu(self):
        return self.fal_yorumu.name.split("/")[-1]

    def __str__(self):
        return "{}-{}".format(self.user, self.id)

    class Meta:
        verbose_name_plural = "Fal Siparişleri"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Mesajın Sahibi")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Hangi Sipariş")
    content = models.TextField(verbose_name="Mesaj İçeriği", max_length=1000)
    message_date = models.DateTimeField(auto_created=True, auto_now=True, verbose_name="Mesaj Zamanı")

    def __str__(self):
        return self.content[:25]

    class Meta:
        verbose_name_plural = "Fal Sipariş Mesajları"


class Image(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Sipariş")
    image = models.ImageField(verbose_name="Fotoğraf", upload_to="photo/")

    def clean_name(self):
        return self.image.name.split("/")[-1]

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name_plural = "Fal Fotoğrafları"


class Comments(models.Model):
    name = models.CharField(verbose_name="İsim", max_length=25)
    comment = models.CharField(verbose_name="Yorum", max_length=1024)

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name_plural = "Müşteri Yorumları"


class BuyOrder(models.Model):
    x = ((1, "Tadımlık"), (3, "Meraklı"), (5, "Bağımlı"))
    y = ((0, "Beklemede"), (1, "Ödeme Geldi"))

    user = models.ForeignKey(User, verbose_name="Satın Alan", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Sipariş Zamanı", auto_now_add=True)
    shopping_cart = models.IntegerField(verbose_name="Sepetteki Ürün", choices=x)
    buy_status = models.IntegerField(verbose_name="Sipariş Durumu", choices=y, default=0)
    readonly = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.buy_status and not self.readonly:
            self.readonly = True
            u = User.objects.get(email=self.user)
            u.fal_credit += self.shopping_cart
            u.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return "SP"+str(self.id+1024)

    def sp_no(self):
        return "SP" + str(self.id + 1024)

    def price(self):
        cart = int(self.shopping_cart)
        if cart == 1:
            return "20₺"

        if cart == 3:
            return "55₺"

        if cart == 5:
            return "90₺"

    class Meta:
        verbose_name_plural = "Kredi Siparişi"
