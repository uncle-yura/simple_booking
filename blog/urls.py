from django.urls import path
from blog import views

urlpatterns = [
    path("", views.BlogListView.as_view(), name = "blog-home"),
    path("new", views.ArticleCreateView.as_view(), name = "new-article"),
    path("<slug:article_slug>/edit", views.ArticleUpdateView.as_view(), name = "edit-article"),
    path("<slug:article_slug>/delete", views.ArticleDeleteView.as_view(), name = "delete-article"),
    path("<slug:article_slug>", views.ArticleDetailView.as_view(), name = "article"),
]
