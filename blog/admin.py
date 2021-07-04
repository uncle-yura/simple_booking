from django.contrib import admin

from blog.models import *


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(SocialShare)
class SocialShareAdmin(admin.ModelAdmin):
    pass
