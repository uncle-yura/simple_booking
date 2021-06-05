from django.db.models.manager import BaseManager
from django.http.response import Http404,HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse

from booking_calendar.models import *
from booking_calendar.forms import *
from booking_calendar.templatetags.time_extras import duration

from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets,GoogleCredentials
from googleapiclient.discovery import build
from dateutil.relativedelta import relativedelta

import datetime
import os
import httplib2

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
        master_form = MasterProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            messages.success(request,('Your profile was successfully updated!'))
        elif master_form.is_valid():
            master_form.save()
            messages.success(request,('Your master profile was successfully updated!'))
        else:
            messages.error(request,('Unable to complete request'))
        return redirect ('user')

    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    master_form = MasterProfileForm(instance=request.user.profile)
    
    return render(request=request,
        template_name="user.html",
        context={"user":request.user,
            "user_form":user_form, 
            "profile_form":profile_form , 
            "master_form":master_form })

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')

FLOW = flow_from_clientsecrets(
CLIENT_SECRETS,
scope='https://www.googleapis.com/auth/calendar',
redirect_uri='http://localhost:8000/booking_calendar/google-oauth2/complete')

@login_required
def gcal_auth(request):
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                request.user.profile.id)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)

@login_required
def gcal_auth_return(request):
    if not xsrfutil.validate_token(settings.SECRET_KEY, bytes(request.GET.get('state'), encoding='utf8'), request.user.profile.id):
        return HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.GET)
    profile = Profile.objects.filter(id=request.user.profile.id).first()
    profile.gcal_key=credential.to_json()
    profile.save()
    
    return redirect('user')

@login_required
def gcal_data_return(request):
    master_id=request.GET.get('master', None)
    if not master_id:
        return JsonResponse({})

    master_profile = Profile.objects.filter(id=master_id).first()
    query_set = Profile.objects.filter(user__groups__name='Master')
    exclude_id = []
    for master in query_set:
        timetable = master.timetable 
        if timetable is not "A" \
            and not (timetable is "M" and master.clients.filter(id__exact=request.user.profile.id).count()>0 ) \
            and not (timetable is "V" and request.user.profile.orders.count()>0):
            exclude_id.append(master.id)
    query_set = query_set.exclude(id__in=exclude_id)
    
    if master_profile in query_set:
        http = httplib2.Http()
        credentials = GoogleCredentials.new_from_json(master_profile.gcal_key)

        http = credentials.authorize(http)
        service = build("calendar", "v3", http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        date_max = datetime.datetime.today() + relativedelta(days=master_profile.booking_time_range)
        date_max = date_max.isoformat() + 'Z'
        page_token = None

        eventsResult = service.events()
        events = eventsResult.list(calendarId=master_profile.gcal_link, 
            pageToken=page_token, 
            singleEvents=True,
            orderBy='startTime',
            timeMin=now, 
            timeMax=date_max).execute()

        response = {'events':{},'prices':{},'range':master_profile.booking_time_range, }

        for price in master_profile.prices.all():
            response['prices'].update({
                price.job.id:{
                    'id':price.job.id,
                    'name':str(price),
                    'price':price.price,
                    'str_time':duration(price.job.time_interval),
                    'time':price.job.time_interval.total_seconds()}})

        for event in events['items']:
            response['events'].update({
                event['id']:{
                    'start':event['start'],
                    'end':event['end'],}})
            page_token = events.get('nextPageToken')

        while page_token:
            for event in events['items']:
                response['events'].update({
                    event['id']:{
                        'start':event['start'],
                        'end':event['end'],}})
                page_token = events.get('nextPageToken')
    else:
        response = {}
    return JsonResponse(response)


class UserDelete(LoginRequiredMixin,DeleteView):
    model = User
    success_url = reverse_lazy('index')
    template_name = 'delete_user.html'


class UserView(PermissionRequiredMixin,LoginRequiredMixin,DetailView):
    model = Profile
    permission_required = 'booking_calendar.view_profile'
    template_name = 'view_user.html'


class OrderCreate(LoginRequiredMixin,CreateView):
    form_class = NewOrderForm
    template_name = 'new_order.html'
    success_url = reverse_lazy('my-orders')

    def get_queryset(self):
        query_set = Profile.objects.filter(user__groups__name='Master')
        exclude_id = []
        for master in query_set:
            timetable = master.timetable 
            if timetable is not "A" \
                and not (timetable is "M" and master.clients.filter(id__exact=self.request.user.profile.id).count()>0 ) \
                and not (timetable is "V" and self.request.user.profile.orders.count()>0):
                exclude_id.append(master.id)
        query_set = query_set.exclude(id__in=exclude_id)
        self.fields['master'].queryset = query_set
        self.fields['work_type'].queryset = BaseManager()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.booking_date < datetime.date.today():
            messages.error(self.request,("We cannot travel to the past.")) 
            return redirect('new-order')
        else:
            self.object.client = self.request.user.profile
            self.object.save()
            messages.success(self.request,('New order created!'))
            return super(OrderCreate, self).form_valid(form)


class OrderView(LoginRequiredMixin,DetailView):
    model = Order
    template_name = 'view_order.html'

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        if self.object.client == self.request.user.profile \
            or self.request.user.groups.filter(name="Master").exists():
            return context
        else:
            raise Http404


class JobsByUserListView(LoginRequiredMixin,ListView):
    model = Order
    template_name = 'orders_list_master.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.jobs.order_by('booking_date')


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
        return self.request.user.profile.clients.order_by('-id')


class PriceListView(LoginRequiredMixin,ListView):
    model = PriceList
    template_name = 'price_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.prices.order_by('-id')


class PublicPriceListView(ListView):
    model = PriceList
    template_name = 'price_list_public.html'
    paginate_by = 10

    def get_queryset(self):
        pricelist = PriceList.objects.filter(profile__id=self.kwargs['pk']).order_by('-id')
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
            messages.success(self.request,('Price created')) 
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

    def delete(self, request, *args, **kwargs):
        messages.success(self.request,('Price deleted')) 
        return super(PriceListDelete, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.profile.prices.all()


class PriceListUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = PriceList
    fields = ['job','price',]
    success_url = reverse_lazy('my-prices')
    template_name = 'update_price.html'
    permission_required = 'booking_calendar.change_pricelist'

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
                messages.success(self.request,('Price updated')) 
        except IntegrityError as e: 
            if 'unique constraint'.lower() in str(e).lower():
                messages.error(self.request,('Price already exist')) 
            return redirect('my-prices')
        else:
            return super(PriceListUpdate, self).form_valid(form)
