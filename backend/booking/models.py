from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as __
from django.core.files import File

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base.storage import UUIDStorage

from dateutil import parser
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image

import pytz
import os


class JobType(models.Model):
    name = models.CharField(
        verbose_name=_("Job name"),
        help_text=_("Enter here job name."),
        max_length=100,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Enter here the text to be displayed as description of job. "),
        max_length=200,
        blank=True,
    )
    time_interval = models.DurationField(
        verbose_name=_("Time"),
        help_text=_("Enter here the time it takes for this job."),
        default=timedelta(minutes=15),
    )
    image = models.ImageField(
        verbose_name=_("Image"),
        help_text=_("Upload your cover image here."),
        upload_to="images/",
        storage=UUIDStorage,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def compress_image(image):
    im = Image.open(image)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im_io = BytesIO()
    im.save(im_io, "webp", quality=80, optimize=True)
    new_image = File(im_io, os.path.splitext(image.name)[0] + ".webp")
    return new_image


class Profile(models.Model):
    class TIME_TABLE(models.TextChoices):
        ALL = "A", _("All")
        MY = "M", _("My clients")
        VERIFIED = "V", _("Verified clients")
        NOBODY = "N", _("Nobody")

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message=_("Phone number must be entered in the format: '+380123456789'."),
    )

    avatar = models.ImageField(
        verbose_name=_("Profile photo"),
        help_text=_("Upload your avatar image here."),
        upload_to="images/",
        storage=UUIDStorage,
        blank=True,
    )
    phone_number = models.CharField(
        verbose_name=_("Phone"),
        help_text=_("Enter your phone number here (Example: +380123456789)"),
        validators=[phone_regex],
        max_length=17,
        blank=True,
    )
    comment = models.TextField(
        verbose_name=_("Comment"),
        help_text=_("Enter the text about the profile owner here."),
        max_length=200,
        blank=True,
    )
    discount = models.DecimalField(
        verbose_name=_("Discount"),
        help_text=_("Enter the profile discount value here."),
        default=0,
        max_digits=2,
        decimal_places=2,
    )
    masters = models.ManyToManyField(
        to="self",
        verbose_name=_("Masters"),
        help_text=_("Your masters listed here."),
        through="Order",
        through_fields=(
            "client",
            "master",
        ),
    )
    clients = models.ManyToManyField(
        to="self",
        verbose_name=_("Clients"),
        help_text=_("Your clients listed here."),
        through="Order",
        through_fields=(
            "master",
            "client",
        ),
    )
    gcal_link = models.CharField(
        verbose_name=_("GCalendar link"),
        help_text=_("Enter your google calendar link here."),
        max_length=200,
        blank=True,
    )
    timetable = models.CharField(
        verbose_name=_("Timetable"),
        help_text=_("Select your current service booking mode."),
        max_length=1,
        choices=TIME_TABLE.choices,
        default=TIME_TABLE.ALL,
    )
    booking_time_delay = models.DurationField(
        verbose_name=_("Booking delay"),
        help_text=_("Enter the minimum delay for booking today."),
        default=timedelta(minutes=60),
    )
    booking_time_range = models.IntegerField(
        verbose_name=_("Booking range"),
        help_text=_("Enter how many days in advance the booking can be made."),
        default=30,
    )
    black_list = models.ManyToManyField(
        to="self",
        verbose_name=_("Black list"),
        help_text=_("Select users who cannot book with you."),
        blank=True,
    )
    white_list = models.ManyToManyField(
        to="self",
        verbose_name=_("White list"),
        help_text=_("Select users who can always book with you."),
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.avatar:
            image = self.avatar
            if image.size > 0.3 * 1024 * 1024:
                self.avatar = compress_image(image)
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}"

    def get_master_calendar(self):
        credentials = service_account.Credentials.from_service_account_info(
            settings.SERVICE_SECRETS, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)
        return service.events()

    def get_future_orders_count(self):
        return self.orders.filter(
            booking_date__gte=datetime.now(pytz.utc), state=Order.STATE_TABLE.ACTIVE
        ).count()

    def get_latest_order_date(self):
        return self.orders.latest("booking_date").booking_date

    def get_uniq_masters(self):
        white_list = Profile.objects.filter(user__groups__name="Master").filter(
            white_list__in=[self]
        )
        return (
            (self.masters.all() | white_list)
            .exclude(black_list__in=[self])
            .order_by()
            .distinct()[:7]
        )

    def get_uniq_clients(self):
        return (
            (self.clients.all() | self.white_list.all())
            .exclude(pk__in=self.black_list.all())
            .order_by()
            .distinct()
        )

    def get_gcal_account(self):
        return settings.SERVICE_SECRETS.get("client_email", "")

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
        unique_together = (
            "profile",
            "job",
        )

    profile = models.ForeignKey(
        to=Profile,
        verbose_name=_("Owner"),
        help_text=_("Select the pricelist owner here."),
        on_delete=models.CASCADE,
        related_name="prices",
    )
    job = models.ForeignKey(
        to=JobType,
        verbose_name=_("Job"),
        help_text=_("Select the job here."),
        on_delete=models.CASCADE,
        related_name="prices",
    )
    price = models.DecimalField(
        verbose_name=_("Price"),
        help_text=_("Enter the price for this job here."),
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.job}"


class Order(models.Model):
    class STATE_TABLE(models.TextChoices):
        ACTIVE = "A", _("Active")
        CANCELED = "C", _("Canceled")

    client = models.ForeignKey(
        to=Profile,
        verbose_name=_("Client"),
        help_text=_("Select the client here."),
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    work_type = models.ManyToManyField(
        to=JobType,
        verbose_name=_("Job"),
        help_text=_("Select the job for this order here."),
    )
    booking_date = models.DateTimeField(
        verbose_name=_("Date"),
        help_text=_("Select your booking date here."),
        null=True,
    )
    client_comment = models.CharField(
        verbose_name=_("Comment"),
        help_text=_("Enter a comment for your booking here."),
        max_length=200,
        blank=True,
    )
    master = models.ForeignKey(
        to=Profile,
        verbose_name=_("Master"),
        help_text=_("Select the master here."),
        on_delete=models.SET_NULL,
        null=True,
        related_name="jobs",
        limit_choices_to={"user__groups__name": "Master"},
    )
    state = models.CharField(
        verbose_name=_("State"),
        help_text=_("Select your booking status here."),
        max_length=1,
        choices=STATE_TABLE.choices,
        default=STATE_TABLE.ACTIVE,
    )
    gcal_event_id = models.CharField(
        verbose_name=_("Event"),
        help_text=_("Google calendar event ID."),
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return f"#{self.id}"

    @classmethod
    def make_new_event(cls, work_type, client_comment, booking_date, profile):
        description = Order.get_event_description(work_type)
        description["text"] += __("\nComment: %s" % client_comment)

        event = {
            "summary": str(profile),
            "description": description["text"],
            "start": {
                "dateTime": booking_date.isoformat(),
            },
            "end": {
                "dateTime": (booking_date + description["time"]).isoformat(),
            },
        }
        return event

    @classmethod
    def get_event_description(cls, work_type):
        description = __("Jobs: ")
        time_interval = timedelta(minutes=0)

        for wt in work_type:
            time_interval += wt.time_interval
            description += "\n" + wt.name

        return {"time": time_interval, "text": description}

    @classmethod
    def check_date(cls, order, master_calendar, work_type):
        if order.booking_date < pytz.UTC.localize(datetime.now() + order.master.booking_time_delay):
            return __("This date is too early.")
        elif order.booking_date > pytz.UTC.localize(
            datetime.today() + timedelta(days=order.master.booking_time_range)
        ):
            return __("This date is too far away.")

        def has_overlap(A_start, A_end, B_start, B_end):
            latest_start = max(A_start, B_start)
            earliest_end = min(A_end, B_end)
            return latest_start < earliest_end

        def parse_time(event):
            return parser.isoparse(event["date"] if "date" in event else event["dateTime"])

        booking_time_interval = Order.get_event_description(work_type)["time"]

        events = {}
        try:
            events = master_calendar.list(
                calendarId=order.master.gcal_link,
                singleEvents=True,
                orderBy="startTime",
                timeMin=datetime.combine(order.booking_date, datetime.min.time()).isoformat() + "Z",
                timeMax=(order.booking_date + booking_time_interval)
                .replace(tzinfo=None)
                .isoformat()
                + "Z",
            ).execute()
        except HttpError:
            return __("Server connection error, unable to get event.")

        page_token = True
        while page_token:
            for event in events["items"]:
                if (
                    has_overlap(
                        order.booking_date,
                        order.booking_date + booking_time_interval,
                        parse_time(event["start"]),
                        parse_time(event["end"]),
                    )
                    and order.gcal_event_id != event["id"]
                ):
                    return __("This date already booked.")
            page_token = events.get("nextPageToken")

        return ""
