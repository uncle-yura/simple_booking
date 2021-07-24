from django.contrib import admin

from .models import *


@admin.register(SocialContact)
class SocialContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactsList)
class ContactsListAdmin(admin.ModelAdmin):
    pass
