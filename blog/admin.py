from django.contrib import admin
from blog.models import Post
from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(SummernoteModelAdmin):
    exclude = ["created_date", "updated_date", "author"]
    list_display = ["title", "tags", "created_date"]
    prepopulated_fields = {"title_url": ("title",)}

admin.site.register(Post, PostAdmin)