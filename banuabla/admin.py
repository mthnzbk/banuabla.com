from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Order, Image, Message, Comments, BuyOrder


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('user_photo', 'email', 'password')}),
        ('Kullanıcı Bilgisi', {'fields': ('referanced_user', 'first_name', 'last_name', "gender", "birth", "fal_credit",
                                          "fal_point")}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'full_name', 'is_active', "gender", "fal_credit", "fal_point", "referanced_user")
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class BuyOrderAdmin(admin.ModelAdmin):
    fieldsets = ()
    readonly_fields = ("shopping_cart", "readonly")


admin.site.register(User, UserAdmin)
admin.site.register(Order)
admin.site.register(Image)
admin.site.register(Message)
admin.site.register(Comments)
admin.site.register(BuyOrder, BuyOrderAdmin)
