# Generated by Django 2.1 on 2018-10-16 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banuabla', '0007_buyorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyorder',
            name='buy_status',
            field=models.IntegerField(choices=[(0, 'Beklemede'), (1, 'Ödeme Geldi')], default=0, verbose_name='Sipariş Durumu'),
            preserve_default=False,
        ),
    ]
