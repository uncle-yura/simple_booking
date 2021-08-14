from django.db import models

from uuid_storage.storage import UUIDStorage
from datetime import datetime


class Photo(models.Model):
    title = models.CharField(
        verbose_name="Title",
        help_text="Enter here the photo title.",
        max_length=200,
        blank=True)
    published = models.DateTimeField(
        verbose_name="Date published",
        help_text="Enter here thr published date.",
        default=datetime.now)
    image = models.ImageField(
        verbose_name="Image",
        help_text="Upload your image here.",
        upload_to='images/',
        storage=UUIDStorage)

    def __str__(self):
        return str(self.published) + self.title
