from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from uuid_storage.storage import UUIDStorage
from datetime import datetime


class Photo(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("Enter here the photo title."),
        max_length=200,
        blank=True)
    published = models.DateTimeField(
        verbose_name=_("Date published"),
        help_text=_("Enter here thr published date."),
        default=datetime.now)
    image = models.ImageField(
        verbose_name=_("Image"),
        help_text=_("Upload your image here."),
        upload_to='images/',
        storage=UUIDStorage)

    def __str__(self):
        to_tz = timezone.get_default_timezone()
        return self.published.astimezone(to_tz).strftime("%Y-%m-%d %H:%M ") + self.title
