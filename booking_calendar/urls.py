from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('user/', views.userpage, name="user"), 
    path('neworder/', views.neworder, name="new-order"), 
    path('register/', views.register, name="register"), 
    path('myorders/', views.OrdersByUserListView.as_view(), name='my-orders'),
]
