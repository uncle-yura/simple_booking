# Generated by Django 3.2.3 on 2022-01-12 11:56

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Enter your email address here.",
                        max_length=254,
                        verbose_name="EMail",
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        help_text="Enter the subject of your email here.",
                        max_length=255,
                        verbose_name="Subject",
                    ),
                ),
                (
                    "message",
                    models.TextField(
                        help_text="Enter the message of your email here.",
                        verbose_name="Message",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContactsList",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Enter here the contact name.",
                        max_length=255,
                        verbose_name="Name",
                    ),
                ),
                (
                    "content",
                    tinymce.models.HTMLField(
                        help_text="Enter the content of the contact block here.",
                        verbose_name="Contact",
                    ),
                ),
                (
                    "content_short",
                    tinymce.models.HTMLField(
                        blank=True,
                        help_text="Enter the content of the short contact block here.",
                        verbose_name="Short info",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SocialContact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "share_name",
                    models.CharField(
                        help_text="Enter here the social contact name.",
                        max_length=20,
                        verbose_name="Name",
                    ),
                ),
                (
                    "share_icon",
                    models.CharField(
                        blank=True,
                        help_text="Enter here icon name from fontawesome "
                        + "(Example: fab fa-instagram).",
                        max_length=20,
                        verbose_name="Icon",
                    ),
                ),
                (
                    "share_text",
                    models.CharField(
                        blank=True,
                        help_text="Enter here the text to be displayed in the link.",
                        max_length=200,
                        verbose_name="Text",
                    ),
                ),
                (
                    "share_url",
                    models.URLField(
                        help_text="Enter here link to social contact account.",
                        verbose_name="URL",
                    ),
                ),
            ],
        ),
    ]
