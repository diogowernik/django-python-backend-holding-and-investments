
from django.core.management.base import BaseCommand
from django.core.management import call_command
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investments.settings")
# django.setup()


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('update_fiis_price')
        call_command('update_total_today_brl')
        call_command('update_fiis_fundamentals')
