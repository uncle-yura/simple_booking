from django.core.management.base import BaseCommand
from django.db import transaction
from ._seed_example_data import SeedExampleData
from ._seed_example_extra_settings import SeedExampleExtraSettings
from ._seed_user_data import SeedUserData


class Command(BaseCommand):
    help = "Seed data for use in development"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Seeding auth_user table")
            seed_users = SeedUserData(self.stdout, self.stderr)
            seed_users.create_users()
            self.stdout.write(self.style.SUCCESS("Done"))

            self.stdout.write("Seeding extra_settings table")
            seed_settings = SeedExampleExtraSettings(self.stdout, self.stderr)
            seed_settings.create_data()
            self.stdout.write(self.style.SUCCESS("Done"))

            self.stdout.write("Seeding data table")
            seed_data = SeedExampleData(self.stdout, self.stderr)
            seed_data.create_data()
            self.stdout.write(self.style.SUCCESS("Done"))
