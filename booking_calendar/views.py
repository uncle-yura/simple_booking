from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages

from booking_calendar.models import *
from booking_calendar.forms import *


def index(request):
    num_jobs = JobType.objects.all().count()
    num_clients = Profile.objects.all().count()

    context = {
        'num_jobs': num_jobs,
        'num_clients': num_clients,
    }

    return render(request, 'index.html', context=context)

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render (request=request, template_name="register.html", context={"form":form})

@login_required
def userpage(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            messages.success(request,('Your profile was successfully updated!'))
        else:
            messages.error(request,('Unable to complete request'))
        return redirect ('user')
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    master_form = MasterProfileForm(instance=request.user.profile)
    
    return render(request=request, template_name="user.html", context={"user":request.user, "user_form":user_form, "profile_form":profile_form , "master_form":master_form })

@login_required
def neworder(request):
    form = NewOrderForm(instance=request.user.profile)
    return render(request=request, template_name="new_order.html", context={"user":request.user, "form":form })


class OrdersByUserListView(LoginRequiredMixin,generic.ListView):
    model = Order
    template_name = 'orders_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user.profile).order_by('booking_date')


class ClientsByUserListView(LoginRequiredMixin,generic.ListView):
    model = Profile
    template_name = 'clients_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.clients.all()


class PriceByUserListView(LoginRequiredMixin,generic.ListView):
    model = PriceList
    template_name = 'price_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.prices.all()

