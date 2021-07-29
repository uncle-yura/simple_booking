from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from tinymce.models import HTMLField
from uuid_storage.storage import UUIDStorage

from datetime import datetime

group, new_group = Group.objects.get_or_create(name='Moderator')


class SocialShare(models.Model):
	share_name = models.CharField(max_length=20)
	share_icon = models.CharField(max_length=20, blank=True)
	share_text = models.CharField(max_length=200)
	share_url = models.URLField(default="")
    
	def __str__(self):
		return self.share_name


class Tag(models.Model):
	tag_name = models.CharField(max_length=20)
	tag_slug = models.SlugField()
    
	def __str__(self):
		return self.tag_name


class Article(models.Model):
	article_title = models.CharField(max_length=200)
	article_published = models.DateTimeField('date published',  default=datetime.now)
	article_image = models.ImageField(upload_to='images/', storage=UUIDStorage)
	article_content = HTMLField()
	article_slug = models.SlugField()
	article_tags = models.ManyToManyField(Tag)
	article_top_posts = models.BooleanField(default=False)

	def __str__(self):
		return self.article_title
