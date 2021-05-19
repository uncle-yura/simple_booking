from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('myorders/', views.OrdersByUserListView.as_view(), name='my-orders'),
]