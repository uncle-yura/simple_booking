from django.shortcuts import render
from django.views import generic
from booking_calendar.models import WorkType, Work
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    # Generate counts of some of the main objects
    num_works = Work.objects.all().count()

    context = {
        'num_works': num_works,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class WorkListView(generic.ListView):
    model = Work
    template_name = 'work_list.html'  
    context_object_name = 'work_list'  
    queryset = Work.objects.order_by('booking_date')

class BookedWorksByUserListView(LoginRequiredMixin,generic.ListView):
    model = Work
    template_name = 'work_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Work.objects.filter(client=self.request.user).order_by('booking_date')