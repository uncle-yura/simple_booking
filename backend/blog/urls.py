from django.urls import path

from .views import (
    BlogListView,
    ArticleCreateView,
    ArticleTagListView,
    ArticleDeleteView,
    ArticleUpdateView,
    ArticleDetailView,
)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog-home"),
    path("new", ArticleCreateView.as_view(), name="new-article"),
    path("<slug:article_slug>/edit", ArticleUpdateView.as_view(), name="edit-article"),
    path("<slug:article_slug>/delete", ArticleDeleteView.as_view(), name="delete-article"),
    path("<slug:article_slug>", ArticleDetailView.as_view(), name="article"),
    path("tag/<slug:article_tags>", ArticleTagListView.as_view(), name="article-tag"),
]
