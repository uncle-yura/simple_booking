from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import Max, Min
from django.contrib.auth.models import User

from verify_email.email_handler import send_verification_email

from .forms import NewUserForm
from booking.models import JobType, Profile
from gallery.models import Photo
from django.utils.translation import gettext as _


def switch_lang(request):
    return render(request, "base/langswitch.html")


def index(request):
    context = {
        "pricelist": JobType.objects.filter(prices__isnull=False)
        .all()
        .annotate(min_price=Min("prices__price"))
        .annotate(max_price=Max("prices__price")),
        "masters": Profile.objects.filter(user__groups__name="Master"),
        "reviews": Photo.objects.all().order_by("-id")[:12],
    }
    return render(request=request, template_name="base/index.html", context=context)


def privacy_policy(request):
    return render(request=request, template_name="base/privacy_policy.html")


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            send_verification_email(request, form)
            messages.warning(
                request,
                _("Click the link in the email message to confirm your email address."),
            )
            return redirect("index")
        messages.error(request, _("Unsuccessful registration. Invalid information."))
    form = NewUserForm
    return render(request=request, template_name="base/register.html", context={"form": form})


class UserDelete(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("index")
    template_name = "base/delete_user.html"
