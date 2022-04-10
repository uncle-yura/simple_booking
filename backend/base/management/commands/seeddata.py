from django.core.management.base import BaseCommand
from django.db import transaction
from ._seed_example_gallery_data import ExampleGalleryData
from ._seed_example_booking_data import ExampleBookingData
from ._seed_example_extra_settings import ExampleExtraSettings
from ._seed_example_user_data import ExampleUserData
from ._seed_example_blog_data import ExampleBlogData
from ._seed_example_contact_data import ExampleContactData


class Command(BaseCommand):
    help = "Seed data for use in development"

    def handle(self, *args, **options):
        with transaction.atomic():
            for data in (
                ExampleUserData,
                ExampleExtraSettings,
                ExampleGalleryData,
                ExampleBookingData,
                ExampleContactData,
                ExampleBlogData,
            ):
                self.stdout.write(f"Seeding {data.__name__}")
                seed_users = data(self.stdout, self.stderr)
                seed_users.create_data()
                self.stdout.write(self.style.SUCCESS("Done"))
