from django.urls import path

from .views import *

urlpatterns = [
    path("", ContactFormView.as_view(), name = "contact"),
]
