from django import template
from django.utils.translation import gettext as _
from datetime import datetime

import pytz

register = template.Library()


@register.filter
def duration(timedelta):
    """ Format a duration field --> 2h and 30 min or only 45 min """
    total_seconds = int(timedelta.total_seconds())
    hours = total_seconds // 3600
    minutes = round((total_seconds % 3600) / 60)
    if minutes == 60:
        hours += 1
        minutes = 0
    if hours and minutes:
        # Display both
        return _('{} h et {} min').format(hours, minutes)
    elif hours:
        # Display only hours
        return _('{} h').format(hours)
    # Display only minutes
    return _('{} min').format(minutes)


@register.filter
def expired(booking_date):
    return booking_date < datetime.now(pytz.utc)
