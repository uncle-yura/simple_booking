from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.widgets import SelectMultiple
from booking_calendar.models import Order, PriceList, Profile


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2",)

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('master', 'work_type', 'booking_date', 'client_comment', )
        widgets = {'booking_date': forms.HiddenInput}


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
        widgets = {'booking_date': forms.HiddenInput, 'master': forms.HiddenInput}


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
