from .models import Tag, SocialShare

def menu(request):
    nav_tags = Tag.objects.all()[:4]
    return { 'nav_tags' : nav_tags,
    }

def share(request):
    share_tags = SocialShare.objects.all()
    return { 'share_tags' : share_tags,
    }
