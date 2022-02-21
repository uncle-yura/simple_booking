from django.views.generic.edit import CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import *
from .models import *


class ContactFormView(CreateView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(ContactFormView, self).get_context_data(**kwargs)
        context['contacts'] = ContactsList.objects.all()
        return context

    def form_valid(self, form):
        if form.send_email():
            messages.success(self.request, _('Message sent'))
        else:
            messages.error(
                self.request, _('Message not sent, please try again later.'))
        return super().form_valid(form)
