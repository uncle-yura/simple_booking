from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

import datetime


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
    discount = models.FloatField(default=0)

    masters = models.ManyToManyField('self', through='Order', through_fields=('client', 'master',),)
    clients = models.ManyToManyField('self', through='Order', through_fields=('master', 'client',),)
    gcal_key = models.CharField(max_length=54, blank=True)
    gcal_link = models.CharField(max_length=42, blank=True)
    timetable = models.CharField(max_length=1, choices=TIME_TABLE.choices, default=TIME_TABLE.ALL)

    def __str__(self):
        return f'{self.user}'

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
        return f'{self.job}, {self.profile}' 


class Order(models.Model):
    client = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="orders")
    work_type = models.ManyToManyField(JobType, help_text='Select a work type for this client')
    booking_date = models.DateField(null=True)
    client_comment = models.CharField(max_length=200, blank=True)
    master = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="jobs", limit_choices_to={'user__groups__name': 'Master'})

    def __str__(self):
        return  f'{self.client}, {self.booking_date}' 



