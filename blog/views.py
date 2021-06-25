from django.shortcuts import render
from django.core.paginator import Paginator

from blog.models import Article

def blog(request):
	blog = Article.objects.all().order_by('-article_published')
	paginator = Paginator(blog, 25)
	page_number = request.GET.get('page')
	blog_obj = paginator.get_page(page_number)
	return render(request=request, template_name="blog/blog.html", context={"blog":blog_obj})

def article(request, article_page):
    article = Article.objects.get(article_slug=article_page)
    return render(request=request, template_name='blog/article.html', context={"article": article})
