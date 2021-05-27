from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('user/', views.userpage, name="user"), 
    path('register/', views.register, name="register"), 

    path('neworder/', views.OrderCreate.as_view(), name="new-order"), 
    path('orders/', views.OrdersByUserListView.as_view(), name='my-orders'),


    path('clients/', views.ClientsByUserListView.as_view(), name='my-clients'),
    path('client/del/<int:pk>', views.UserDelete.as_view(), name='user-delete'),
    path('client/<int:pk>', views.UserView.as_view(), name='user-view'),

    path('pricelist/', views.PriceListView.as_view(), name='my-prices'),
    path('pricelist/<int:pk>', views.PublicPriceListView.as_view(), name='public-prices'),
    path('price/edit/<int:pk>', views.PriceListUpdate.as_view(), name='price-update'),
    path('price/add/', views.PriceListCreate.as_view(), name='price-add'),
    path('price/del/<int:pk>', views.PriceListDelete.as_view(), name='price-delete'),
]
