from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class JobType(models.Model):
    name = models.CharField(max_length=100, help_text='Enter a work type')
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.name}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+380123456789'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    comment = models.CharField(max_length=200, blank=True)
    is_master = models.BooleanField(default=False)
    gcal_key = models.CharField(max_length=54, blank=True)
    gcal_link = models.CharField(max_length=42, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        if not hasattr(instance, "profile"):
            Profile.objects.create(user=instance)
        instance.profile.save()


class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    work_type = models.ManyToManyField(JobType, help_text='Select a work type for this client')
    booking_date = models.DateField(null=True)
    client_comment = models.CharField(max_length=200, blank=True)
    master = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="jobs")

    def __str__(self):
        return  f'{self.client.first_name}, {self.booking_date}' 



