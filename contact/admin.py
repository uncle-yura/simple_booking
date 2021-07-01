from django.contrib import admin

from .models import Contact, ContactsList


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactsList)
class ContactsListAdmin(admin.ModelAdmin):
    pass
