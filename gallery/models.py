from django.db import models

from uuid_storage.storage import UUIDStorage

from datetime import datetime


class Photo(models.Model):
	title = models.CharField(max_length=200, blank=True)
	published = models.DateTimeField('date published',  default=datetime.now)
	image = models.ImageField(upload_to='images/', storage=UUIDStorage)

	def __str__(self):
		return str(self.published) + self.title
