from django.db import models
from django.utils.translation import gettext_lazy  as _

from tinymce.models import HTMLField
from uuid_storage.storage import UUIDStorage
from datetime import datetime


class SocialShare(models.Model):
    share_name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Enter here social share name."),
        max_length=20,
        )
    share_icon = models.CharField(
        verbose_name=_("Icon"),
        help_text=_("Enter here icon name from fontawesome (Example: fab fa-facebook)."),
        max_length=20,
        blank=True,
        )
    share_text = models.CharField(
        verbose_name=_("Text"),
        help_text=_("Enter here the text to be displayed in the link (Example: &t=New post )."),
        max_length=200,
        )
    share_url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("Enter here link to social share account. (Example: https://www.facebook.com/sharer/sharer.php?u=)"),
        )

    def __str__(self):
        return self.share_name


class Tag(models.Model):
    tag_name = models.CharField(
        verbose_name=_("Tag"),
        help_text=_("Enter here the tag name."),
        max_length=20,
        )
    tag_slug = models.SlugField(
        verbose_name=_("Link"),
        help_text=_("Enter here the link of tag (Example: photos)"),
        )

    def __str__(self):
        return self.tag_name


def generate_slug():
    return datetime.now().strftime("%d%m%Y%H%M%S_post")


class Article(models.Model):
    article_title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("Enter here the article title."),
        max_length=200,
        )
    article_published = models.DateTimeField(
        verbose_name=_("Date published"),
        help_text=_("Enter here thr published date."),
        default=datetime.now,
        )
    article_image = models.ImageField(
        verbose_name=_("Cover"),
        help_text=_("Upload article cover here."),
        upload_to='images/',
        storage=UUIDStorage,
        )
    article_content = HTMLField(
        verbose_name=_("Article"),
        help_text=_("Enter here the article content."),
        )
    article_slug = models.SlugField(
        verbose_name=_("Link"),
        help_text=_("Enter here the link of article (Example: happy_new_post)."),
        default=generate_slug,
        )
    article_tags = models.ManyToManyField(
        to=Tag,
        verbose_name=_("Tags"),
        help_text=_("Select tags for this post."),
        blank=True,
        )
    article_top_posts = models.BooleanField(
        verbose_name=_("Top"),
        help_text=_("Activate if you want to pin this post on the main page."),
        default=False,
        )

    def __str__(self):
        return self.article_title
