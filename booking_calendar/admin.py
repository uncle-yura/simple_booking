from booking_calendar.models import Work, WorkType
from django.contrib import admin

# Register your models here.

class WorksInline(admin.TabularInline):
    model = Work


# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'phone_number',)
#     fieldsets = (
#         ('Main', {
#             'fields': ('first_name', 'last_name', 'phone_number')
#         }),
#         ('Additional', {
#             'fields': ('comment',)
#         }),
#     )
#     #inlines = [WorksInline]


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('client', 'booking_date',)
    list_filter = ('booking_date',)


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    pass
