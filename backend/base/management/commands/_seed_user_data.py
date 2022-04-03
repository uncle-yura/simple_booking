import io
import os
import random
import py_avataaars

from django.conf import settings
from django.contrib.auth.models import User, Group


def save_random_avatar_image(filename):
    bytes = io.BytesIO()

    def r(enum_):
        return random.choice(list(enum_))

    avatar = py_avataaars.PyAvataaar(
        style=py_avataaars.AvatarStyle.CIRCLE,
        # style=py_avataaars.AvatarStyle.TRANSPARENT,
        skin_color=r(py_avataaars.SkinColor),
        hair_color=r(py_avataaars.HairColor),
        facial_hair_type=r(py_avataaars.FacialHairType),
        facial_hair_color=r(py_avataaars.Color),
        top_type=r(py_avataaars.TopType),
        hat_color=r(py_avataaars.Color),
        mouth_type=r(py_avataaars.MouthType),
        eye_type=r(py_avataaars.EyesType),
        eyebrow_type=r(py_avataaars.EyebrowType),
        nose_type=r(py_avataaars.NoseType),
        accessories_type=r(py_avataaars.AccessoriesType),
        clothe_type=r(py_avataaars.ClotheType),
        clothe_color=r(py_avataaars.Color),
        clothe_graphic_type=r(py_avataaars.ClotheGraphicType),
    )
    avatar.render_png_file(bytes)

    with open(filename, "wb") as outfile:
        outfile.write(bytes.getbuffer())


class SeedUserData:
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

    def create_users(self):
        self._create_user("staff", True, True)
        master = self._create_user("master", False, False)
        moderator = self._create_user("moderator", False, False)
        self._create_user("member", False, False)

        master_group = Group.objects.get(name="Master")
        master_group.user_set.add(master)

        moderator_group = Group.objects.get(name="Moderator")
        moderator_group.user_set.add(moderator)
