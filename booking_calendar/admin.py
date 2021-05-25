from booking_calendar.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class OrdersInline(admin.TabularInline):
    model = Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('client', 'booking_date',)
    list_filter = ('booking_date', 'master')


@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    pass


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)