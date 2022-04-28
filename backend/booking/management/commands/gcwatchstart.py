from django.core.management.base import BaseCommand

from booking.models import Profile


class Command(BaseCommand):
    help = "Start watch for changes to Events resources."

    def handle(self, *args, **options):
        masters = Profile.objects.filter(user__groups__name="Master")
        for master in masters:
            result = master.start_watch_calendar()
            self.stdout.write(
                f"Profile #{master.id} calendar watcher status: "
                + f"{'Started' if result else 'Error'}"
            )
