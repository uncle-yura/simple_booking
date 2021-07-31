from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from .models import Article,Tag


class BlogListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    paginate_by = 10
    ordering = ['-article_published']


class ArticleTagListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    paginate_by = 10

    def get_queryset(self):
        tag = Tag.objects.get(tag_slug=self.kwargs['article_tags'])
        return super().get_queryset().filter(article_tags=tag).order_by('-article_published')


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    model = Article
    permission_required = 'blog.add_article'
    template_name = 'update_form.html'
    fields = '__all__'
    success_url = reverse_lazy('blog-home')


    class Media:
        js = ('tinymce/tinymce.min.js', 
            'django_tinymce/init_tinymce.js',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'New article'
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article.html'
    slug_field = 'article_slug'
    slug_url_kwarg = 'article_slug'


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    model = Article
    permission_required = 'blog.change_article'
    template_name = 'update_form.html'
    slug_field = 'article_slug'
    slug_url_kwarg = 'article_slug'
    fields = '__all__'
    success_url = reverse_lazy('blog-home')


    class Media:
        js = ('tinymce/tinymce.min.js', 
            'django_tinymce/init_tinymce.js',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update article:'
        return context


class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    model = Article
    permission_required = 'blog.delete_article'
    template_name = 'delete_form.html'
    slug_field = 'article_slug'
    slug_url_kwarg = 'article_slug'
    fields = '__all__'
    success_url = reverse_lazy('blog-home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Delete article'
        return context
