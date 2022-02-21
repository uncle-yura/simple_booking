from .models import *


def menu(request):
    nav_tags = Tag.objects.all()[:4]
    return {'nav_tags': nav_tags,
            }


def share(request):
    share_tags = SocialShare.objects.all()
    return {'share_tags': share_tags,
            }


def top_posts(request):
    top_posts = Article.objects.filter(article_top_posts=True).all()
    return {'top_posts': top_posts,
            }
