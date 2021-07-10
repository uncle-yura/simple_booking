from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.models import inlineformset_factory
from django.forms.widgets import SelectMultiple, Select

from .models import Order, PriceList, Profile

from datetime import datetime

import math


class PriceOwnerOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().profile == self.request.user.profile


class OrderOwnerOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().client == self.request.user.profile


class OrderMasterSelect(Select):
    def __init__(self, attrs=None, choices=()):
        super(Select, self).__init__(attrs, choices=choices)

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if value:
            master = Profile.objects.filter(id=int(value.value)).first()
            option['attrs']['range'] = int(master.booking_time_range)
            option['attrs']['delay'] = str(math.floor((datetime.now() + master.booking_time_delay).timestamp()*1000))
        return option


class CustomSelectMultiple(SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        super(SelectMultiple, self).__init__(attrs, choices=choices)

    def render(self, name, value, attrs=None, renderer=None):
        widgets_html = super(SelectMultiple, self).render(name, value, attrs, renderer)
        widgets_html +=  "<script>let select_input = $('#id_"+name+"');" + '''
            select_input.select2({width: '100%'});
            select_input.attr("data-container", "body");
            select_input.attr("data-toggle", "popover");
            select_input.attr("data-placement", "right");
            </script>
            '''
        return widgets_html

class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('master', 'work_type', 'booking_date', 'client_comment', )
        widgets = {'booking_date': forms.HiddenInput, 'master':OrderMasterSelect}

    class Media:
        js = ('booking/js/ajax.js',
                'booking/js/events.js',
                'booking/js/functions.js',
                'booking/js/eventClass.js')

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super(NewOrderForm, self).__init__(*args, **kwargs)
        query_set = Profile.objects.filter(user__groups__name='Master')
        exclude_id = []
        for master in query_set:
            timetable = master.timetable
            if timetable is not "A" \
                and not (timetable is "M" and master.get_uniq_clients().filter(id__exact=request.user.profile.id).count()>0 ) \
                and not (timetable is "V" and request.user.profile.orders.count()>0) \
                or master.black_list.filter(id__exact=request.user.profile.id).count()>0 :
                exclude_id.append(master.id)
        query_set = query_set.exclude(id__in=exclude_id)
        self.fields['master'].queryset = query_set


class OrderPriceMultiSelect(SelectMultiple):
    def __init__(self, attrs=None, choices=(), custom_attrs={}):
        super(SelectMultiple, self).__init__(attrs, choices=choices)
        self.item_time = dict(custom_attrs['time'])
        self.item_price = dict(custom_attrs['price'])

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if value:
            option['attrs']['time'] = int(self.item_time[args[0]].total_seconds())
            option['attrs']['price'] = self.item_price[args[0]]
        return option


class EditOrderForm(NewOrderForm):
    class Meta(NewOrderForm.Meta):
        widgets = {'booking_date': forms.HiddenInput, 'master': forms.HiddenInput,}

    class Media:
        js = ('booking/js/ajax.js',
                'booking/js/events.js',
                'booking/js/functions.js',
                'booking/js/eventClass.js')


class CancelOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('state',)
        widgets = {'state': forms.HiddenInput,}


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class ProfileForm(forms.ModelForm):
    class Meta: 
        model = Profile
        fields = ('phone_number', )        


class MasterProfileForm(forms.ModelForm):
    class Meta: 
        model = Profile
        fields = ('timetable', 'booking_time_range', 'booking_time_delay', 'gcal_link', )


PriceListFormSet = inlineformset_factory(
    Profile, PriceList, fields = ('job','price',), extra=1)
