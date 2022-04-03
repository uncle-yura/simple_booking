# Generated by Django 3.2.3 on 2022-01-12 11:56

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import base.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter here job name.', max_length=100, verbose_name='Job name')),
                ('description', models.TextField(blank=True, help_text='Enter here the text to be displayed as description of job. ', max_length=200, verbose_name='Description')),
                ('time_interval', models.DurationField(default=datetime.timedelta(seconds=900), help_text='Enter here the time it takes for this job.', verbose_name='Time')),
                ('image', models.ImageField(blank=True, help_text='Upload your cover image here.', storage=base.storage.UUIDStorage, upload_to='images/', verbose_name='Image')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(help_text='Select your booking date here.', null=True, verbose_name='Date')),
                ('client_comment', models.CharField(blank=True, help_text='Enter a comment for your booking here.', max_length=200, verbose_name='Comment')),
                ('state', models.CharField(choices=[('A', 'Active'), ('C', 'Canceled')], default='A', help_text='Select your booking status here.', max_length=1, verbose_name='State')),
                ('gcal_event_id', models.CharField(blank=True, help_text='Google calendar event ID.', max_length=30, verbose_name='Event')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, help_text='Upload your avatar image here.', storage=base.storage.UUIDStorage, upload_to='images/', verbose_name='Profile photo')),
                ('phone_number', models.CharField(blank=True, help_text='Enter your phone number here (Example: +380123456789)', max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+380123456789'.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Phone')),
                ('comment', models.TextField(blank=True, help_text='Enter the text about the profile owner here.', max_length=200, verbose_name='Comment')),
                ('discount', models.DecimalField(decimal_places=2, default=0, help_text='Enter the profile discount value here.', max_digits=2, verbose_name='Discount')),
                ('gcal_link', models.CharField(blank=True, help_text='Enter your google calendar link here.', max_length=200, verbose_name='GCalendar link')),
                ('timetable', models.CharField(choices=[('A', 'All'), ('M', 'My clients'), ('V', 'Verified clients'), ('N', 'Nobody')], default='A', help_text='Select your current service booking mode.', max_length=1, verbose_name='Timetable')),
                ('booking_time_delay', models.DurationField(default=datetime.timedelta(seconds=3600), help_text='Enter the minimum delay for booking today.', verbose_name='Booking delay')),
                ('booking_time_range', models.IntegerField(default=30, help_text='Enter how many days in advance the booking can be made.', verbose_name='Booking range')),
                ('black_list', models.ManyToManyField(blank=True, help_text='Select users who cannot book with you.', related_name='_booking_profile_black_list_+', to='booking.Profile', verbose_name='Black list')),
                ('clients', models.ManyToManyField(help_text='Your clients listed here.', related_name='_booking_profile_clients_+', through='booking.Order', to='booking.Profile', verbose_name='Clients')),
                ('masters', models.ManyToManyField(help_text='Your masters listed here.', related_name='_booking_profile_masters_+', through='booking.Order', to='booking.Profile', verbose_name='Masters')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('white_list', models.ManyToManyField(blank=True, help_text='Select users who can always book with you.', related_name='_booking_profile_white_list_+', to='booking.Profile', verbose_name='White list')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='client',
            field=models.ForeignKey(help_text='Select the client here.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='booking.profile', verbose_name='Client'),
        ),
        migrations.AddField(
            model_name='order',
            name='master',
            field=models.ForeignKey(help_text='Select the master here.', limit_choices_to={'user__groups__name': 'Master'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs', to='booking.profile', verbose_name='Master'),
        ),
        migrations.AddField(
            model_name='order',
            name='work_type',
            field=models.ManyToManyField(help_text='Select the job for this order here.', to='booking.JobType', verbose_name='Job'),
        ),
        migrations.CreateModel(
            name='PriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, help_text='Enter the price for this job here.', max_digits=10, verbose_name='Price')),
                ('job', models.ForeignKey(help_text='Select the job here.', on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='booking.jobtype', verbose_name='Job')),
                ('profile', models.ForeignKey(help_text='Select the pricelist owner here.', on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='booking.profile', verbose_name='Owner')),
            ],
            options={
                'unique_together': {('profile', 'job')},
            },
        ),
    ]
