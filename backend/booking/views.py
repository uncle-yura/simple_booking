from django.conf import settings
from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    CreateView,
    DetailView,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.forms.models import modelform_factory
from django.utils.translation import gettext as _
from booking.decorators import check_orders_count, is_master, require_ajax

from booking.forms import (
    CancelOrderForm,
    CustomSelectMultiple,
    DiscountForm,
    EditOrderForm,
    MasterProfileForm,
    NewOrderForm,
    OrderOwnerOnlyMixin,
    OrderPriceMultiSelect,
    PriceListFormSet,
    PriceOwnerOnlyMixin,
    ProfileForm,
    UserForm,
)
from booking.models import Order, PriceList, Profile


from .templatetags.time_extras import duration

from googleapiclient.errors import HttpError
from secrets import compare_digest

from datetime import datetime, date, timedelta

import math


@login_required
def userpage(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        master_form = MasterProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            messages.success(request, _("Your profile was successfully updated!"))
        elif master_form.is_valid():
            master_form.save()
            messages.success(request, _("Your master profile was successfully updated!"))
        else:
            messages.error(request, _("Unable to complete request"))
        return redirect("user")

    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    master_form = MasterProfileForm(instance=request.user.profile)

    return render(
        request=request,
        template_name="booking/user.html",
        context={
            "user": request.user,
            "user_form": user_form,
            "profile_form": profile_form,
            "master_form": master_form,
        },
    )


@csrf_exempt
@require_POST
def gcal_event_webhook(request):
    given_token = request.headers.get("x-goog-channel-token", "")
    if not compare_digest(given_token, settings.SERVICE_WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            "Incorrect token in header.",
            content_type="text/plain",
        )

    if request.headers.get("x-goog-resource-state", "") == "exists":
        id = int(request.headers.get("x-goog-channel-id"))
        master_profile = Profile.objects.filter(id=id).first()
        try:
            events = (
                master_profile.get_master_calendar()
                .list(
                    calendarId=master_profile.gcal_link,
                    singleEvents=True,
                    updatedMin=datetime.today() - timedelta(minutes=1),
                )
                .execute()
            )
        except HttpError:
            return _("Server connection error, unable to get event.")

        page_token = True
        while page_token:
            event_dict = {event["id"]: event for event in events["items"]}
            orders = Order.objects.filter(gcal_event_id__in=event_dict.keys()).all()
            for order in orders:
                order.booking_date = event_dict[order.gcal_event_id]["start"]
                order.save()
            page_token = events.get("nextPageToken")

    return HttpResponse("OK.", content_type="text/plain")


@login_required
@require_ajax
def gcal_data_return(request):
    master_id = request.GET.get("master", None)
    if not master_id:
        return JsonResponse(
            {
                "success": False,
                "msg": [
                    _("Master not selected."),
                ],
            }
        )

    order_id = request.GET.get("order", None)
    master_profile = Profile.objects.filter(id=master_id).first()
    query_set = Profile.objects.filter(user__groups__name="Master")
    exclude_id = []
    for master in query_set:
        timetable = master.timetable
        if (
            timetable is not Profile.TIME_TABLE.ALL[0]
            and not (
                timetable is Profile.TIME_TABLE.MY[0]
                and master.clients.filter(id__exact=request.user.profile.id).count() > 0
            )
            and not (
                timetable is Profile.TIME_TABLE.VERIFIED[0]
                and request.user.profile.orders.count() > 0
            )
        ):
            exclude_id.append(master.id)
    query_set = query_set.exclude(id__in=exclude_id)

    if master_profile in query_set:
        now = datetime.combine(date.today(), datetime.min.time())

        date_max = datetime.today() + timedelta(days=master_profile.booking_time_range)
        date_max = date_max.isoformat() + "Z"
        page_token = None

        eventsResult = master_profile.get_master_calendar()
        events = {}

        try:
            events = eventsResult.list(
                calendarId=master_profile.gcal_link,
                pageToken=page_token,
                singleEvents=True,
                orderBy="startTime",
                timeMin=now.isoformat() + "Z",
                timeMax=date_max,
            ).execute()
        except HttpError:
            return JsonResponse(
                {
                    "success": False,
                    "msg": [
                        _("This master has closed booking access."),
                    ],
                }
            )

        response = {
            "success": True,
            "events": {},
            "prices": {},
            "range": master_profile.booking_time_range,
            "delay": str(
                math.floor((datetime.now() + master_profile.booking_time_delay).timestamp() * 1000)
            ),
        }

        for price in master_profile.prices.all():
            response["prices"].update(
                {
                    price.job.id: {
                        "id": price.job.id,
                        "name": str(price),
                        "price": price.price,
                        "str_time": duration(price.job.time_interval),
                        "time": price.job.time_interval.total_seconds(),
                    }
                }
            )

        for event in events["items"]:
            if event["id"] == order_id:
                continue
            response["events"].update(
                {
                    event["id"]: {
                        "start": event["start"],
                        "end": event["end"],
                    }
                }
            )
            page_token = events.get("nextPageToken")

        while page_token:
            for event in events["items"]:
                if event["id"] == order_id:
                    continue
                response["events"].update(
                    {
                        event["id"]: {
                            "start": event["start"],
                            "end": event["end"],
                        }
                    }
                )
            page_token = events.get("nextPageToken")
    else:
        return JsonResponse(
            {
                "success": False,
                "msg": [
                    _("It is impossible to get a reservation from this master."),
                ],
            }
        )
    return JsonResponse(response)


class UserView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "booking/view_user.html"

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)

        context["discount_form"] = DiscountForm(instance=self.object.user.profile)

        if (
            self.object == self.request.user.profile
            or self.request.user.groups.filter(name="Master").exists()
        ):
            return context
        else:
            raise Http404


@method_decorator(login_required, name="dispatch")
@method_decorator(check_orders_count, name="dispatch")
class OrderCreate(CreateView):
    form_class = NewOrderForm
    template_name = "booking/new_order.html"
    success_url = reverse_lazy("my-orders")

    def get_form_kwargs(self):
        kwargs = super(OrderCreate, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        master_calendar = self.object.master.get_master_calendar()
        work_type = form.cleaned_data["work_type"]

        error_message = Order.check_date(self.object, master_calendar, work_type)
        if not error_message:
            event = Order.make_new_event(
                work_type,
                self.object.client_comment,
                self.object.booking_date,
                self.request.user.profile,
            )

            try:
                event_id = master_calendar.insert(
                    calendarId=self.object.master.gcal_link, body=event
                ).execute()
            except HttpError:
                messages.error(self.request, _("Server connection error, unable to add new event."))
                return redirect("new-order")

            self.object.client = self.request.user.profile
            self.object.gcal_event_id = event_id["id"]
            self.object.save()

            messages.success(self.request, _("New order created!"))
            return super(OrderCreate, self).form_valid(form)
        else:
            messages.error(self.request, error_message)
            return redirect("new-order")


class OrderUpdate(OrderOwnerOnlyMixin, UpdateView):
    model = Order
    form_class = EditOrderForm
    success_url = reverse_lazy("my-orders")
    template_name = "booking/update_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_id"] = self.object.gcal_event_id
        return context

    def get_form_kwargs(self):
        kwargs = super(OrderUpdate, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_form(self):
        form = super().get_form(form_class=self.form_class)

        master = form.fields["master"].queryset.first()

        query_set = form.fields["work_type"].queryset
        include_id = []
        for price in master.prices.all():
            include_id.append(price.job.id)
        query_set = query_set.filter(id__in=include_id)
        form.fields["work_type"].queryset = query_set

        choices = form.fields["work_type"].choices
        form.fields["work_type"].widget = OrderPriceMultiSelect(
            choices=choices,
            attrs={"preloaded": True},
            custom_attrs={
                "time": query_set.values_list("name", "time_interval"),
                "price": master.prices.all().values_list("job__name", "price"),
            },
        )

        form.fields["master"].widget.attrs.update(
            {
                "range": int(master.booking_time_range),
                "delay": str(
                    math.floor((datetime.now() + master.booking_time_delay).timestamp() * 1000)
                ),
            }
        )
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.gcal_event_id:
            master_calendar = self.object.master.get_master_calendar()
            work_type = form.cleaned_data["work_type"]

            error_message = Order.check_date(self.object, master_calendar, work_type)
            if not error_message:
                event = Order.make_new_event(
                    work_type,
                    self.object.client_comment,
                    self.object.booking_date,
                    self.request.user.profile,
                )

                try:
                    master_calendar.update(
                        calendarId=self.object.master.gcal_link,
                        eventId=self.object.gcal_event_id,
                        body=event,
                    ).execute()
                except HttpError:
                    messages.error(
                        self.request,
                        _("Server connection error, unable to update event."),
                    )
                    return redirect("my-orders")

                self.object.save()
                messages.success(self.request, _("Order data updated!"))
                return super(OrderUpdate, self).form_valid(form)
            else:
                messages.error(self.request, error_message)
                return redirect("my-orders")
        else:
            messages.error(self.request, _("This event canceled by master."))
            return redirect("my-orders")


class OrderCancel(OrderOwnerOnlyMixin, UpdateView):
    model = Order
    form_class = CancelOrderForm
    success_url = reverse_lazy("my-orders")
    template_name = "delete_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Cancel order")
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.gcal_event_id:
            master_calendar = self.object.master.get_master_calendar()

            try:
                master_calendar.delete(
                    calendarId=self.object.master.gcal_link,
                    eventId=self.object.gcal_event_id,
                ).execute()
            except HttpError:
                messages.error(self.request, _("Server connection error, unable to delete event."))
                return redirect("my-orders")

        self.object.state = Order.STATE_TABLE.CANCELED
        self.object.save()
        messages.success(self.request, _("Order canceled."))

        return super(OrderCancel, self).form_valid(form)


class OrderView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "booking/view_order.html"

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        if (
            self.object.client == self.request.user.profile
            or self.request.user.groups.filter(name="Master").exists()
        ):
            return context
        else:
            raise Http404


@method_decorator(is_master, name="dispatch")
class JobsByUserListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "booking/orders_list_master.html"
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.jobs.order_by("-booking_date")


class OrdersByUserListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "booking/orders_list_user.html"
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.orders.order_by("-booking_date")


class ClientsByUserListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "booking/clients_list_user.html"
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.get_uniq_clients().order_by("-id")


@method_decorator(login_required, name="dispatch")
@method_decorator(is_master, name="dispatch")
class WhiteListUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy("my-clients")
    template_name = "update_form.html"
    form_class = modelform_factory(
        model=Profile,
        widgets={"white_list": CustomSelectMultiple},
        fields=[
            "white_list",
        ],
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("White list")
        return context

    def get_object(self):
        return Profile.objects.get(pk=self.request.user.profile.id)


@method_decorator(login_required, name="dispatch")
@method_decorator(is_master, name="dispatch")
class BlackListUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy("my-clients")
    template_name = "update_form.html"
    form_class = modelform_factory(
        model=Profile,
        widgets={"black_list": CustomSelectMultiple},
        fields=[
            "black_list",
        ],
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Black list")
        return context

    def get_object(self):
        return Profile.objects.get(pk=self.request.user.profile.id)

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.jobs.filter(client__in=form.cleaned_data["black_list"]).count() > 0:
            messages.error(
                self.request,
                _("It is impossible to blacklist a client while he has an open order."),
            )
            return redirect("my-clients")

        self.object.save()
        return super(BlackListUpdate, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(is_master, name="dispatch")
class PriceListView(LoginRequiredMixin, ListView):
    model = PriceList
    template_name = "booking/price_list_user.html"
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.prices.order_by("-id")


class PublicPriceListView(ListView):
    model = PriceList
    template_name = "booking/price_list_public.html"
    paginate_by = 10

    def get_queryset(self):
        pricelist = PriceList.objects.filter(profile__id=self.kwargs["pk"]).order_by("-id")
        if pricelist.count() > 0:
            return pricelist
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(PublicPriceListView, self).get_context_data(**kwargs)
        context["name"] = Profile.objects.filter(id=self.kwargs["pk"]).first()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(is_master, name="dispatch")
class PriceListCreate(LoginRequiredMixin, CreateView):
    model = PriceList
    fields = [
        "job",
        "price",
    ]
    template_name = "update_form.html"
    success_url = reverse_lazy("my-prices")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Add price")
        return context

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.profile = self.request.user.profile
            self.object.save()
            messages.success(self.request, _("Price created"))
        except IntegrityError as e:
            if "unique constraint".lower() in str(e).lower():
                messages.error(self.request, _("Price already exist"))
            return redirect("my-prices")
        else:
            return super(PriceListCreate, self).form_valid(form)


class PriceListDelete(PriceOwnerOnlyMixin, DeleteView):
    model = PriceList
    success_url = reverse_lazy("my-prices")
    template_name = "delete_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Delete price")
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Price deleted"))
        return super(PriceListDelete, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.profile.prices.all()


class PriceListUpdate(PriceOwnerOnlyMixin, UpdateView):
    model = PriceList
    fields = [
        "job",
        "price",
    ]
    success_url = reverse_lazy("my-prices")
    template_name = "update_form.html"

    def get_context_data(self, **kwargs):
        data = super(PriceListUpdate, self).get_context_data(**kwargs)

        data["form_title"] = _("Update price:")

        if self.request.POST:
            data["pricelist"] = PriceListFormSet(self.request.POST, instance=self.object.profile)
        else:
            data["pricelist"] = PriceListFormSet(instance=self.object.profile)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pricelist = context["pricelist"]
        try:
            self.object = form.save()

            if pricelist.is_valid():
                pricelist.instance = self.object
                pricelist.save()
                messages.success(self.request, _("Price updated"))
        except IntegrityError as e:
            if "unique constraint".lower() in str(e).lower():
                messages.error(self.request, _("Price already exist"))
            return redirect("my-prices")
        else:
            return super(PriceListUpdate, self).form_valid(form)
