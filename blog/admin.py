from django.contrib import admin

from blog.models import *

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass
