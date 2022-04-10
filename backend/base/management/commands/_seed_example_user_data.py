import os

from django.conf import settings
from django.contrib.auth.models import User, Group

from base.services import save_random_avatar_image


class ExampleUserData:
    @staticmethod
    def _create_user(name, is_staff, is_superuser):
        user, created = User.objects.get_or_create(
            email=f"{name}@booking.local",
            username=f"booking-{name}",
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        if created:
            user.set_password("booking")
            user.save()

            save_random_avatar_image(
                os.path.join(settings.MEDIA_ROOT, f"avatar-{name}.png")
            )
            user.profile.avatar = f"avatar-{name}.png"
            user.profile.save()
        return user

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def create_data(self):
        self._create_user("staff", True, True)
        master = self._create_user("master", False, False)
        moderator = self._create_user("moderator", False, False)
        self._create_user("member", False, False)

        master_group = Group.objects.get(name="Master")
        master_group.user_set.add(master)

        moderator_group = Group.objects.get(name="Moderator")
        moderator_group.user_set.add(moderator)
