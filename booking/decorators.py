from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from django.contrib import messages

from extra_settings.models import Setting


def require_ajax(func):
    def decorator(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)

    return decorator


def check_orders_count(func):
    def decorator(request, *args, **kwargs):
        order_limit = Setting.get('FUTURE_ORDERS_LIMIT', default=3)

        if request.user.profile.get_future_orders_count() >= order_limit:
            messages.error(request, "You have too many booked orders.")
            return redirect('index')
        return func(request, *args, **kwargs)

    return decorator


def is_master(func):
    def decorator(request, *args, **kwargs):
        if not request.user.groups.filter(name='Master').exists():
            return redirect('index')
        return func(request, *args, **kwargs)

    return decorator
