from django.http.response import Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from booking_calendar.models import *
from booking_calendar.forms import *
from booking_calendar.decorators import *
from booking_calendar.templatetags.time_extras import duration

from googleapiclient.errors import HttpError

from datetime import datetime,date,timedelta

import math


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


@login_required
@require_ajax
def gcal_data_return(request):
    master_id=request.GET.get('master', None)
    if not master_id:
        return JsonResponse({'success': False, 'msg':["Master not selected.",]})

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
        now = datetime.combine(date.today(), 
            datetime.min.time())

        date_max = datetime.today() + timedelta(days=master_profile.booking_time_range)
        date_max = date_max.isoformat() + 'Z'
        page_token = None

        eventsResult = master_profile.get_master_calendar()
        events = {}

        try:
            events = eventsResult.list(calendarId=master_profile.gcal_link, 
                pageToken=page_token, 
                singleEvents=True,
                orderBy='startTime',
                timeMin=now.isoformat() + 'Z', 
                timeMax=date_max).execute()
        except HttpError:
            return JsonResponse({'success': False, 'msg':["This master has closed booking access.",]})

        response = {
            'success': True,
            'events':{},
            'prices':{},
            'range':master_profile.booking_time_range,
            'delay':str(math.floor((datetime.now() + master_profile.booking_time_delay).timestamp()*1000)), }

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
        return JsonResponse({'success': False, 'msg':["It is impossible to get a reservation from this master.",]})
    return JsonResponse(response)


class UserDelete(LoginRequiredMixin,DeleteView):
    model = User
    success_url = reverse_lazy('index')
    template_name = 'delete_user.html'


class UserView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'view_user.html'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        if self.object == self.request.user.profile \
            or self.request.user.groups.filter(name="Master").exists():
            return context
        else:
            raise Http404


class OrderCreate(LoginRequiredMixin,CreateView):
    form_class = NewOrderForm
    template_name = 'new_order.html'
    success_url = reverse_lazy('my-orders')

    @method_decorator(check_orders_count)
    def dispatch(self,request,*args,**kwargs):
        return super(OrderCreate,self).dispatch(request,*args,**kwargs)

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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        master_calendar = self.object.master.get_master_calendar()
        work_type = form.cleaned_data['work_type']

        error_message = Order.check_date(self.object, master_calendar, work_type)
        if not error_message:
            event = Order.make_new_event(work_type,
                 self.object.client_comment, 
                 self.object.booking_date, 
                 self.request.user.profile)

            try:
                event_id = master_calendar.insert(calendarId=self.object.master.gcal_link,body=event).execute()
            except HttpError:
                messages.error(self.request,("Server connection error, unable to add new event.")) 
                return redirect('new-order')

            self.object.client = self.request.user.profile
            self.object.gcal_event_id = event_id['id']
            self.object.save()

            messages.success(self.request,('New order created!'))
            return super(OrderCreate, self).form_valid(form)
        else:
            messages.error(self.request,error_message) 
            return redirect('new-order')


class OrderUpdate(OrderOwnerOnlyMixin, UpdateView):
    model = Order
    form_class = EditOrderForm
    success_url = reverse_lazy('my-orders')
    template_name = 'update_order.html'

    def get_form(self):
        form = super().get_form(form_class=self.form_class)
        
        master = form.fields['master'].queryset.first()
        
        query_set = form.fields['work_type'].queryset
        include_id = []
        for price in master.prices.all():
            include_id.append(price.job.id)
        query_set = query_set.filter(id__in=include_id)
        form.fields['work_type'].queryset = query_set

        choices = form.fields['work_type'].choices
        form.fields['work_type'].widget = OrderPriceMultiSelect(choices=choices, attrs={'preloaded':True}, custom_attrs={
            'time':query_set.values_list('name','time_interval'),
            'price':master.prices.all().values_list('job__name','price')})

        form.fields['master'].widget.attrs.update({'range': int(master.booking_time_range),
            'delay': str(math.floor((datetime.now() + master.booking_time_delay).timestamp()*1000))})
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.gcal_event_id:
            master_calendar = self.object.master.get_master_calendar()
            work_type = form.cleaned_data['work_type']

            error_message = Order.check_date(self.object, master_calendar, work_type)
            if not error_message:
                event = Order.make_new_event(work_type,
                    self.object.client_comment, 
                    self.object.booking_date, 
                    self.request.user.profile)

                try:
                    master_calendar.update(calendarId=self.object.master.gcal_link, eventId=self.object.gcal_event_id, body=event).execute()
                except HttpError:
                    messages.error(self.request,("Server connection error, unable to update event.")) 
                    return redirect('my-orders')  

                self.object.save()
                messages.success(self.request,('Order data updated!'))
                return super(OrderUpdate, self).form_valid(form)    
            else:
                messages.error(self.request,error_message) 
                return redirect('my-orders')      
        else:              
            messages.error(self.request,("This event canceled by master.")) 
            return redirect('my-orders')


class OrderCancel(OrderOwnerOnlyMixin, UpdateView):
    model = Order
    form_class = CancelOrderForm
    success_url = reverse_lazy('my-orders')
    template_name = 'cancel_order.html'


    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.gcal_event_id:
            master_calendar = self.object.master.get_master_calendar()

            try:
                master_calendar.delete(calendarId=self.object.master.gcal_link, eventId=self.object.gcal_event_id).execute()
            except HttpError:
                messages.error(self.request,("Server connection error, unable to delete event.")) 
                return redirect('my-orders')  
  
        self.object.state = Order.STATE_TABLE.CANCELED
        self.object.save()
        messages.success(self.request,('Order canceled.')) 

        return super(OrderCancel, self).form_valid(form)


class OrderView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'view_order.html'

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        if self.object.client == self.request.user.profile \
            or self.request.user.groups.filter(name="Master").exists():
            return context
        else:
            raise Http404


class JobsByUserListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders_list_master.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.jobs.order_by('-booking_date')


class OrdersByUserListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.orders.order_by('-booking_date')


class ClientsByUserListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'clients_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.get_uniq_clients().order_by('-id')


class PriceListView(LoginRequiredMixin, ListView):
    model = PriceList
    template_name = 'price_list_user.html'
    paginate_by = 10

    @method_decorator(is_master)
    def dispatch(self,request,*args,**kwargs):
        return super(PublicPriceListView,self).dispatch(request,*args,**kwargs)

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


class PriceListCreate(LoginRequiredMixin, CreateView):
    model = PriceList
    fields = ['job','price',]
    template_name = 'add_price.html'
    success_url = reverse_lazy('my-prices')

    @method_decorator(is_master)
    def dispatch(self,request,*args,**kwargs):
        return super(PriceListCreate,self).dispatch(request,*args,**kwargs)

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


class PriceListDelete(PriceOwnerOnlyMixin, DeleteView):
    model = PriceList
    success_url = reverse_lazy('my-prices')
    template_name = 'delete_price.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request,('Price deleted')) 
        return super(PriceListDelete, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.profile.prices.all()


class PriceListUpdate(PriceOwnerOnlyMixin, UpdateView):
    model = PriceList
    fields = ['job','price',]
    success_url = reverse_lazy('my-prices')
    template_name = 'update_price.html'

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
