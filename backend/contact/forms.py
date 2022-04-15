from django.forms import ModelForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _

from captcha.fields import ReCaptchaField
from extra_settings.models import Setting
from .models import Contact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"

    if settings.RECAPTCHA_ACTIVE:
        captcha = ReCaptchaField()

    def send_email(self):
        mail = send_mail(
            self.cleaned_data["subject"],
            _("Message from {}: {}").format(
                self.cleaned_data["email"], self.cleaned_data["message"]
            ),
            settings.EMAIL_HOST_USER,
            [
                Setting.get("CONTACT_EMAIL"),
            ],
            fail_silently=False,
        )
        return mail
