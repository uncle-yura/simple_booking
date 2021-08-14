"""simple_booking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bootstrap_customizer import urls as bootstrap_customizer_urls

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path(settings.ADMIN_URL+'/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('verification/', include('verify_email.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('bootstrap_customizer/', include(bootstrap_customizer_urls)),
    path('social-auth/', include('social_django.urls', namespace="social")),
]

urlpatterns += [
    path('', include('base.urls')),
]

urlpatterns += [
    path('booking/', include('booking.urls')),
]

urlpatterns += [
    path('blog/', include('blog.urls')),
]

urlpatterns += [
    path('contact/', include('contact.urls')),
]

urlpatterns += [
    path('gallery/', include('gallery.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
