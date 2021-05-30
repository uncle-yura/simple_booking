from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory, inlineformset_factory
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
        fields = ('timetable', 'gcal_link', )


PriceListFormSet = inlineformset_factory(
    Profile, PriceList, fields = ('job','price',), extra=1)
