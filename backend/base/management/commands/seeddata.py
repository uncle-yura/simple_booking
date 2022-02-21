from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ._seed_example_data import SeedExampleData


class Command(BaseCommand):
    help = "Seed data for use in development"

    def handle(self, *args, **options):
        self.stdout.write("Seeding auth_user table")
        with transaction.atomic():
            admin, created=User.objects.get_or_create(
                email="staff@booking.local",
                username="booking-staff",
                is_staff=True,
                is_superuser=True,
            )
            if created:
                admin.set_password("booking")
                admin.save()

            user, created=User.objects.get_or_create(
                email="member@booking.local",
                username="booking-member",
                is_staff=False,
                is_superuser=False,
            )
            if created:
                user.set_password("booking")
                user.save()

            seed_data = SeedExampleData(self.stdout, self.stderr)
            seed_data.create_data()

            self.stdout.write(self.style.SUCCESS("Done"))