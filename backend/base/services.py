import io
import os
import random
from django.conf import settings
import py_avataaars


def get_example_assets_folder():
    return os.path.join(settings.BASE_DIR, "base", "management", "commands", "assets")


def get_lorem_ipsum():
    return "<p>Lorem <b>ipsum</b> dolor sit amet, consectetur adipiscing elit, \
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
nisi ut aliquip ex ea commodo consequat.</p> <p>Duis aute irure dolor in \
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla \
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in \
culpa qui officia deserunt mollit anim id est laborum.</p>"


def save_random_avatar_image(filename):
    bytes = io.BytesIO()

    def r(enum_):
        return random.choice(list(enum_))

    avatar = py_avataaars.PyAvataaar(
        style=r(py_avataaars.AvatarStyle),
        background_color=r(py_avataaars.Color),
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
