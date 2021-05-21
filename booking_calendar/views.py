from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages

from booking_calendar.models import Order, Profile, JobType
from booking_calendar.forms import NewUserForm, UserForm, ProfileForm


def index(request):
    num_jobs = JobType.objects.all().count()
    num_clients = Profile.objects.all().count()
    num_masters = Profile.objects.all().filter(is_master=True).count()

    context = {
        'num_jobs': num_jobs,
        'num_clients': num_clients,
        'num_masters': num_masters,
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

def userpage(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
        elif profile_form.is_valid():
            profile_form.save()
        return redirect ('user')
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    return render(request=request, template_name="user.html", context={"user":request.user, "user_form":user_form, "profile_form":profile_form })

class OrdersByUserListView(LoginRequiredMixin,generic.ListView):
    model = Order
    template_name = 'orders_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user).order_by('booking_date')