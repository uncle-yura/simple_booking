from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('works/', views.WorkListView.as_view(), name='works'),
]

urlpatterns += [
    path('myworks/', views.BookedWorksByUserListView.as_view(), name='my-works'),
]