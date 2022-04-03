import os
import shutil

from django.conf import settings
from extra_settings.models import Setting


class SeedExampleExtraSettings:
    FILENAME = "favicon.png"
    DATA = (
        (
            "ABOUT_US",
            Setting.TYPE_TEXT,
            "<p>Lorem <b>ipsum</b> dolor sit amet, consectetur adipiscing elit, \
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
nisi ut aliquip ex ea commodo consequat.</p> <p>Duis aute irure dolor in \
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla \
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in \
culpa qui officia deserunt mollit anim id est laborum.</p>",
        ),
        ("FAVICON_LOGO", Setting.TYPE_IMAGE, FILENAME),
        ("FOOTER_BLOCK", Setting.TYPE_TEXT, "<!-- Escape block in footer -->"),
        ("FOOTER_COPYRIGHT", Setting.TYPE_STRING, "Copyright (C) Uncle-Yura"),
        (
            "FOOTER_DISCLOSURE",
            Setting.TYPE_TEXT,
            "<p>Lorem <b>ipsum</b> dolor sit amet, consectetur adipiscing elit, \
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
nisi ut aliquip ex ea commodo consequat.</p>",
        ),
        (
            "FOOTER_FOLLOW",
            Setting.TYPE_TEXT,
            "<!-- Escape block after follow block -->",
        ),
        ("FOOTER_LOGO", Setting.TYPE_IMAGE, FILENAME),
        ("HEADER_BLOCK", Setting.TYPE_TEXT, "<!-- Escape block in header -->"),
        (
            "HOW_TO_FIND",
            Setting.TYPE_TEXT,
            '<iframe src="https://www.google.com/maps/\
embed?pb=!1m18!1m12!1m3!1d2540.801446267819!2d30.5194681006375!3d50.444798928654905!\
2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40d4ce5670881b1d%3A0xf37306f112c\
fa22c!2z0JrQuNGX0LIsINCj0LrRgNCw0ZfQvdCwLCAwMjAwMA!5e0!3m2!1suk!2sus!4v1648989135754\
!5m2!1suk!2sus" width="600" height="450" style="border:0;" allowfullscreen="" \
loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
        ),
        ("NAVBAR_LOGO", Setting.TYPE_IMAGE, FILENAME),
        ("PRICE_CURRENCY", Setting.TYPE_STRING, "usd"),
        ("SITE_COUNTRY", Setting.TYPE_STRING, "USA"),
        ("SITE_NAME", Setting.TYPE_STRING, "Booking DEV"),
        ("SITE_TITLE", Setting.TYPE_STRING, "Booking site dev"),
    )

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def create_data(self, *args, **kwargs):
        assets = os.path.join(
            settings.BASE_DIR, "base", "management", "commands", "assets"
        )

        shutil.copyfile(
            os.path.join(
                assets,
                self.FILENAME,
            ),
            os.path.join(settings.MEDIA_ROOT, self.FILENAME),
        )
        for name, type, value in self.DATA:
            if not Setting.get(name):
                setting_obj = Setting(
                    name=name,
                    value_type=type,
                    value=value,
                )
                setting_obj.save()
