from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField


class SocialContact(models.Model):
    share_name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Enter here the social contact name."),
        max_length=20,
    )
    share_icon = models.CharField(
        verbose_name=_("Icon"),
        help_text=_("Enter here icon name from fontawesome (Example: fab fa-instagram)."),
        max_length=20,
        blank=True,
    )
    share_text = models.CharField(
        verbose_name=_("Text"),
        help_text=_("Enter here the text to be displayed in the link."),
        max_length=200,
        blank=True,
    )
    share_url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("Enter here link to social contact account."),
    )

    def __str__(self):
        return self.share_name


class ContactsList(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Enter here the contact name."),
        max_length=255,
    )
    content = HTMLField(
        verbose_name=_("Contact"),
        help_text=_("Enter the content of the contact block here."),
    )
    content_short = HTMLField(
        verbose_name=_("Short info"),
        help_text=_("Enter the content of the short contact block here."),
        blank=True,
    )

    def __str__(self):
        return self.name


class Contact(models.Model):
    email = models.EmailField(
        verbose_name=_("EMail"),
        help_text=_("Enter your email address here."),
    )
    subject = models.CharField(
        verbose_name=_("Subject"),
        help_text=_("Enter the subject of your email here."),
        max_length=255,
    )
    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Enter the message of your email here."),
    )

    def __str__(self):
        return self.email
