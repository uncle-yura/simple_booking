from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import Max, Min

from verify_email.email_handler import send_verification_email

from .forms import *
from booking.models import JobType

def index(request):
    context={'pricelist':JobType.objects.all().annotate(min_price=Min('prices__price')).annotate(max_price=Max('prices__price'))}
    return render(request=request, template_name='base/index.html', context=context)


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = send_verification_email(request, form)
            messages.warning(request, "Click the link in the email message to confirm your email address.")
            return redirect('index')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render (request=request, template_name='base/register.html', context={"form":form})


class UserDelete(LoginRequiredMixin,DeleteView):
    model = User
    success_url = reverse_lazy('index')
    template_name = 'base/delete_user.html'
