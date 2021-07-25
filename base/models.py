from django.db import models

from django.contrib.auth.models import User

User.__str__ = lambda user_instance: user_instance.first_name + " " + user_instance.last_name if user_instance.first_name and user_instance.last_name else user_instance.username
