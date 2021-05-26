from django.http.response import Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy

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


class OrdersByUserListView(LoginRequiredMixin,ListView):
    model = Order
    template_name = 'orders_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.orders.order_by('booking_date')


class ClientsByUserListView(LoginRequiredMixin,ListView):
    model = Profile
    template_name = 'clients_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.clients.all()


class PriceListView(LoginRequiredMixin,ListView):
    model = PriceList
    template_name = 'price_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.prices.all()


class PublicPriceListView(ListView):
    model = PriceList
    template_name = 'price_list_public.html'
    paginate_by = 10

    def get_queryset(self):
        pricelist = PriceList.objects.filter(profile__id=self.kwargs['pk'])
        if pricelist.count() > 0:
            return pricelist
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(PublicPriceListView, self).get_context_data(**kwargs)
        context['name'] = Profile.objects.filter(id=self.kwargs['pk']).first()
        return context


class PriceListCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    permission_required = 'booking_calendar.add_pricelist'
    model = PriceList
    fields = ['job','price',]
    template_name = 'add_price.html'
    success_url = reverse_lazy('my-prices')

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.profile = self.request.user.profile
            self.object.save()
        except IntegrityError as e: 
            if 'unique constraint'.lower() in str(e).lower():
               messages.error(self.request,('Price already exist')) 
            return redirect('my-prices')
        else:
            return super(PriceListCreate, self).form_valid(form)


class PriceListDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = PriceList
    success_url = reverse_lazy('my-prices')
    template_name = 'delete_price.html'
    permission_required = 'booking_calendar.delete_pricelist'

    def get_queryset(self):
        return self.request.user.profile.prices.all()


class PriceListUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = PriceList
    fields = ['job','price',]
    success_url = reverse_lazy('my-prices')
    template_name = 'update_price.html'
    permission_required = 'booking_calendar.change_pricelist'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.prices.all()

    def get_context_data(self, **kwargs):
        data = super(PriceListUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['pricelist'] = PriceListFormSet(self.request.POST, instance=self.object.profile)
        else:
            data['pricelist'] = PriceListFormSet(instance=self.object.profile)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pricelist = context['pricelist']
        try:
            self.object = form.save()

            if pricelist.is_valid():
                pricelist.instance = self.object
                pricelist.save()
        except IntegrityError as e: 
            if 'unique constraint'.lower() in str(e).lower():
                messages.error(self.request,('Price already exist')) 
            return redirect('my-prices')
        else:
            return super(PriceListUpdate, self).form_valid(form)
