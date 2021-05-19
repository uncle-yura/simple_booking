from django.shortcuts import render
from django.views import generic
from booking_calendar.models import Order, Profile, JobType
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    # Generate counts of some of the main objects
    num_jobs = JobType.objects.all().count()
    num_clients = Profile.objects.all().count()
    num_masters = Profile.objects.all().filter(is_master=True).count()

    context = {
        'num_jobs': num_jobs,
        'num_clients': num_clients,
        'num_masters': num_masters,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class OrdersByUserListView(LoginRequiredMixin,generic.ListView):
    model = Order
    template_name = 'orders_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user).order_by('booking_date')