from django.core.management.base import BaseCommand
from django.db import transaction
from ._seed_example_data import SeedExampleData
from ._seed_user_data import SeedUserData

class Command(BaseCommand):
    help = "Seed data for use in development"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Seeding auth_user table")
            SeedUserData(self.stdout, self.stderr).create_users()

            seed_data = SeedExampleData(self.stdout, self.stderr)
            seed_data.create_data()
            self.stdout.write(self.style.SUCCESS("Done"))
