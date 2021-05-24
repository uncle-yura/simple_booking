from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from booking_calendar.models import Order, Profile


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
        fields = ('phone_number', 'gcal_key', 'gcal_link',)

class RestrictedProfileForm(ProfileForm):
    class Meta(ProfileForm.Meta):
        exclude = ( 'gcal_key', 'gcal_link',)

class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('client',)

    def __init__(self, *args, **kwargs):
        super(NewOrderForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['master'].queryset = Profile.objects.filter(id__in=kwargs['instance'].masters.all())

