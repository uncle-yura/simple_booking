from django.urls import path
from blog import views

urlpatterns = [
    path("", views.blog, name = "blog-home"),
    path("<article_page>", views.article, name = "article"),
]
