# Generated by Django 2.1 on 2018-08-16 20:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banuabla', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='referanced_user',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=True, to=settings.AUTH_USER_MODEL, verbose_name='Refansı'),
        ),
    ]
