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
        fields = ( 'gcal_key', 'gcal_link', 'timetable', )


PriceListFormSet = inlineformset_factory(
    Profile, PriceList, fields = ('job','price',), extra=1)


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('client',)

    def __init__(self, *args, **kwargs):
        super(NewOrderForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            query_set = Profile.objects.filter(user__groups__name='Master')
            exclude_id = []
            for master in query_set:
                timetable = master.timetable 
                if timetable is not "A" \
                   and not (timetable is "M" and master.clients.filter(id__exact=kwargs['instance'].id).count()>0 ) \
                    and not (timetable is "V" and kwargs['instance'].orders.count()>0):
                    exclude_id.append(master.id)
            query_set = query_set.exclude(id__in=exclude_id)
            self.fields['master'].queryset = query_set
