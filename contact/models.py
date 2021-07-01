from django.db import models

from tinymce.models import HTMLField

class ContactsList(models.Model):
    name = models.CharField(max_length=255)
    content = HTMLField()
    content_short = HTMLField(null=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.email
