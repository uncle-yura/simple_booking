from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class WorkType(models.Model):
    name = models.CharField(max_length=100, help_text='Enter a work type')
    comment = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.name}'

class Work(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    work_type = models.ManyToManyField(WorkType, help_text='Select a work type for this client')
    booking_date = models.DateField(null=True)
    comment = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return  f'{self.client.first_name}, {self.booking_date}' 

#class Client(models.Model):
#    first_name = models.CharField(max_length=100)
#    last_name = models.CharField(max_length=100, blank=True)
#    phone_number = models.CharField(max_length=13)
#    comment = models.CharField(max_length=200, blank=True)
#
#    def __str__(self):
#        return f'{self.first_name} {self.last_name}'
