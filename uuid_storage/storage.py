from django.core.files.storage import FileSystemStorage

import uuid
import os


class UUIDStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        filename, file_extension = os.path.splitext(name)
        dirname = os.path.dirname(name)
        name = os.path.join(dirname, str(uuid.uuid4())+file_extension)
        return super(UUIDStorage, self).get_available_name(name, **kwargs)
