from django.core.management import BaseCommand
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from bootstrap_customizer.models import BootstrapTheme,SiteBootstrapTheme


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default theme"

    def handle(self, *args, **options):
        theme, _ = BootstrapTheme.objects.get_or_create(name="default")
        current_site = Site.objects.get_current()

        try:
            bootstrap_theme = SiteBootstrapTheme.objects.get(site=current_site)
            bootstrap_theme.bootstrap_theme=theme
            bootstrap_theme.save()
        except ObjectDoesNotExist:
            SiteBootstrapTheme.objects.create(site=current_site, bootstrap_theme=theme)
