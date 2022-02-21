from django.contrib import admin

from .models import *


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass
