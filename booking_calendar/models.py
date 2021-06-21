from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dateutil import parser
from datetime import datetime,timedelta

import pytz
import json

class JobType(models.Model):
    name = models.CharField(max_length=100, help_text='Enter a work type')
    description = models.CharField(max_length=200, blank=True)
    time_interval = models.DurationField(default=timedelta(minutes=15))

    def __str__(self):
        return f'{self.name}'

SCOPES = ["https://www.googleapis.com/auth/calendar"]

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
    booking_time_delay = models.DurationField(default=timedelta(minutes=60))
    booking_time_range = models.IntegerField(default=30)

    def __str__(self):
        return f'{self.user}'

    def get_master_calendar(self):
        credentials = service_account.Credentials.from_service_account_file(settings.SERVICE_SECRETS, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        return service.events()

    def get_future_orders_count(self):
        return self.orders.filter(booking_date__gte=datetime.now(pytz.utc)).count()

    def get_latest_order_date(self):
        return self.orders.latest('booking_date').booking_date

    def get_uniq_masters(self):
        return self.masters.order_by().distinct()

    def get_uniq_clients(self):
        return self.clients.order_by().distinct()

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

    @classmethod
    def make_new_event(cls, work_type, client_comment, booking_date, profile):
        description = Order.get_event_description(work_type)
        description['text'] += "\nComment: " + client_comment

        event = {
            'summary': str(profile),
            'description': description['text'],
            'start': {
                'dateTime': booking_date.isoformat(),
            },
            'end': {
                'dateTime': (booking_date + description['time']).isoformat(),
            }
        }
        return event

    @classmethod
    def get_event_description(cls, work_type):
        description = "Jobs: "
        time_interval = timedelta(minutes=0)

        for wt in work_type:
            time_interval += wt.time_interval
            description += '\n' + wt.name

        return {'time':time_interval, 'text':description}

    @classmethod
    def check_date(cls, order, master_calendar, work_type):
        if order.booking_date <  pytz.UTC.localize(datetime.now() + order.master.booking_time_delay):
            return "This date is too early."
        elif order.booking_date > pytz.UTC.localize(datetime.today() + timedelta(days=order.master.booking_time_range)):
            return "This date is too far away."
         
        def has_overlap(A_start, A_end, B_start, B_end):
            latest_start = max(A_start, B_start)
            earliest_end = min(A_end, B_end)
            return latest_start < earliest_end

        def parse_time(event):
            return parser.isoparse(event['date'] if 'date' in event else event['dateTime'])

        booking_time_interval = Order.get_event_description(work_type)['time']

        events = {}
        try:
            events = master_calendar.list(calendarId=order.master.gcal_link,  
                singleEvents=True,
                orderBy='startTime',
                timeMin=datetime.combine(order.booking_date, datetime.min.time()).isoformat() + 'Z', 
                timeMax=(order.booking_date+booking_time_interval).replace(tzinfo=None).isoformat() + 'Z').execute()
        except HttpError:
            return "Server connection error, unable to get event."

        page_token = True
        while page_token:
            for event in events['items']:
                if has_overlap(order.booking_date, order.booking_date + booking_time_interval, parse_time(event['start']), parse_time(event['end'])):
                    return "This date already booked."
            page_token = events.get('nextPageToken')

        return ""
