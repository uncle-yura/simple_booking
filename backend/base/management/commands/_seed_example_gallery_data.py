import os

from django.conf import settings
from base.services import save_random_avatar_image
from gallery.models import Photo


class ExampleGalleryData:
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def create_data(self):
        for index in range(10):
            photo, created = Photo.objects.get_or_create(id=index)
            if created:
                name = f"photo-{index}.png"
                save_random_avatar_image(os.path.join(settings.MEDIA_ROOT, name))
                photo.title = f"Example gallery photo #{index}"
                photo.image = name
                photo.save()
