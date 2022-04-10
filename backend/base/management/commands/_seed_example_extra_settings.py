import os
import shutil

from django.conf import settings
from base.services import get_example_assets_folder, get_lorem_ipsum
from extra_settings.models import Setting


class ExampleExtraSettings:
    FILENAME = "favicon.png"
    DATA = (
        (
            "ABOUT_US",
            Setting.TYPE_TEXT,
            get_lorem_ipsum(),
        ),
        ("FAVICON_LOGO", Setting.TYPE_IMAGE, FILENAME),
        ("FOOTER_BLOCK", Setting.TYPE_TEXT, "<!-- Escape block in footer -->"),
        ("FOOTER_COPYRIGHT", Setting.TYPE_STRING, "Copyright (C) Uncle-Yura"),
        (
            "FOOTER_DISCLOSURE",
            Setting.TYPE_TEXT,
            get_lorem_ipsum()[:248],
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
!5m2!1suk!2sus" height="450" style="border:0;" allowfullscreen="" \
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

    def create_data(self):
        shutil.copyfile(
            os.path.join(
                get_example_assets_folder(),
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
