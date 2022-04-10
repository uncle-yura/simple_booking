from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("user/del/<int:pk>", views.UserDelete.as_view(), name="user-delete"),
]
