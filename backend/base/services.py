import os
import random
import py_avataaars

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from django.conf import settings
from django.core.files import File


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


def save_generated_image(filename, text):
    colors = ["black", "white", "blue", "red", "green", "yellow", "orange", "brown"]
    img = Image.new("RGB", (200, 400), color=random.choice(colors))

    fnt = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    d.text((10, 100), text, font=fnt, fill=random.choice(colors))

    img.save(filename)


def save_random_avatar_image(filename):
    bytes = BytesIO()

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


def compress_image(image):
    im = Image.open(image)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im_io = BytesIO()
    im.save(im_io, "webp", quality=80, optimize=True)
    new_image = File(im_io, os.path.splitext(image.name)[0] + ".webp")
    return new_image
