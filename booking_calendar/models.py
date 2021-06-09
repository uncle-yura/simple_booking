from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import datetime
import pytz
import json

class JobType(models.Model):
    name = models.CharField(max_length=100, help_text='Enter a work type')
    description = models.CharField(max_length=200, blank=True)
    time_interval = models.DurationField(default=datetime.timedelta(minutes=15))

    def __str__(self):
        return f'{self.name}'


class Profile(models.Model):
    class TIME_TABLE(models.TextChoices):
        ALL = 'A', 'All'
        MY = 'M', 'My clients'
        VERIFIED = 'V', 'Verified clients'
        NOBODY = 'N', 'Nobody'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+380123456789'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    comment = models.CharField(max_length=200, blank=True)
    discount = models.DecimalField(default=0, max_digits=2, decimal_places=2)

    masters = models.ManyToManyField('self', through='Order', through_fields=('client', 'master',),)
    clients = models.ManyToManyField('self', through='Order', through_fields=('master', 'client',),)
    gcal_key = models.CharField(max_length=200, blank=True)
    gcal_link = models.CharField(max_length=200, blank=True)
    timetable = models.CharField(max_length=1, choices=TIME_TABLE.choices, default=TIME_TABLE.ALL)
    booking_time_delay = models.DurationField(default=datetime.timedelta(minutes=60))
    booking_time_range = models.IntegerField(default=30)

    def __str__(self):
        return f'{self.user}'

    def get_future_orders_count(self):
        return self.orders.filter(booking_date__gte=datetime.datetime.now(pytz.utc)).count()

    def get_latest_order_date(self):
        return self.orders.latest('booking_date').booking_date

    def get_uniq_masters(self):
        return self.masters.order_by().distinct()

    def get_gcal_account(self):
        with open(settings.SERVICE_SECRETS) as json_file:
            data = json.load(json_file)
            return data['client_email']

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        if not hasattr(instance, "profile"):
            Profile.objects.create(user=instance)
        instance.profile.save()


class PriceList(models.Model):
    class Meta:
        unique_together = ('profile', 'job',)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="prices")
    job = models.ForeignKey(JobType, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.job}' 


class Order(models.Model):
    class STATE_TABLE(models.TextChoices):
        NEW = 'N', 'New'
        CANCELED = 'D', 'Deleted'
        VERIFIED = 'V', 'Verified'
        COMPLETED = 'C', 'Completed'

    client = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="orders")
    work_type = models.ManyToManyField(JobType, help_text='Select a work type for this client')
    booking_date = models.DateTimeField(null=True)
    client_comment = models.CharField(max_length=200, blank=True)
    master = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="jobs", limit_choices_to={'user__groups__name': 'Master'})
    state = models.CharField(max_length=1, choices=STATE_TABLE.choices, default=STATE_TABLE.NEW)
    gcal_event_id = models.CharField(max_length=30, blank=True)


    def __str__(self):
        return  f'{self.client}, {self.booking_date}' 
