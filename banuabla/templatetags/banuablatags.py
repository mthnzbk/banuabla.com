from django import template
from banuabla.models import Order

register = template.Library()


@register.simple_tag(name="gelen_kutusu")
def gelen_kutusu():
    return Order.objects.filter(order_status__exact=False).count()


@register.filter
def sub(value, arg):
    return int(value) - int(arg)
