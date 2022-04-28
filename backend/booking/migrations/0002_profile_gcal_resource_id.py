# Generated by Django 3.2.3 on 2022-04-24 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="gcal_resource_id",
            field=models.CharField(
                blank=True,
                help_text="Event watch resourceId.",
                max_length=200,
                verbose_name="GCalendar resourceId",
            ),
        ),
    ]
