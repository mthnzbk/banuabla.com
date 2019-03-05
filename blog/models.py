from django.db import models
from banuabla.models import User

class Post(models.Model):
    publish = models.BooleanField(verbose_name="Yayında", default=False)
    author = models.ForeignKey(User, verbose_name="Yazar", on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255, verbose_name="Başlık")
    title_url = models.SlugField(max_length=255, verbose_name="Url")
    content = models.TextField(verbose_name="İçerik")
    tags = models.CharField(verbose_name="Etiketler", max_length=500)
    created_date = models.DateTimeField(auto_created=True, auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Yazılar"