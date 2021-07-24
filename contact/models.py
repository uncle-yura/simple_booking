from django.db import models

from tinymce.models import HTMLField


class SocialContact(models.Model):
    share_name = models.CharField(max_length=20)
    share_icon = models.CharField(max_length=20, blank=True)
    share_text = models.CharField(max_length=200, blank=True)
    share_url = models.URLField(default="")

    def __str__(self):
        return self.share_name


class ContactsList(models.Model):
    name = models.CharField(max_length=255)
    content = HTMLField()
    content_short = HTMLField(null=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.email
