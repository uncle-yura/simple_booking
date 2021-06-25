from django.db import models

from tinymce.models import HTMLField


class Article(models.Model):
	article_title = models.CharField(max_length=200)
	article_published = models.DateTimeField('date published')
	article_image = models.ImageField(upload_to='images/')
	article_content = HTMLField()
	article_slug = models.SlugField()

	def __str__(self):
		return self.article_title
