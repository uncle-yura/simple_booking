from django.urls import path

from .views import *

urlpatterns = [
    path("", PhotoListView.as_view(), name="gallery-home"),
    path("new", PhotoCreateView.as_view(), name="new-photo"),
    path("<int:pk>/delete", PhotoDeleteView.as_view(), name="delete-photo"),
    path("<int:pk>/edit", PhotoUpdateView.as_view(), name="edit-photo"),
    path("<int:pk>", PhotoDetailView.as_view(), name="photo"),
]
