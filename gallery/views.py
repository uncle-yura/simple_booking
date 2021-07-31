from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from .models import *


class PhotoListView(PermissionRequiredMixin,ListView):
    model = Photo
    permission_required = 'gallery.view_photo'
    template_name = 'gallery/photo_list.html'
    paginate_by = 10
    ordering = ['-published']


class PhotoCreateView(PermissionRequiredMixin, CreateView):
    model = Photo
    permission_required = 'gallery.add_photo'
    template_name = 'update_form.html'
    fields = '__all__'
    success_url = reverse_lazy('gallery-home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'New photo'
        return context


class PhotoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Photo
    permission_required = 'gallery.change_photo'
    template_name = 'update_form.html'
    fields = '__all__'
    success_url = reverse_lazy('gallery-home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update photo'
        return context


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'gallery/photo.html'


class PhotoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Photo
    permission_required = 'gallery.delete_photo'
    template_name = 'delete_form.html'
    fields = '__all__'
    success_url = reverse_lazy('gallery-home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Delete photo'
        return context
