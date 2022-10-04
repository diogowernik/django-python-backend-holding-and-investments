
from django.core.management.base import BaseCommand
from django.core.management import call_command
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investments.settings")
# django.setup()


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('update_fiis_price')
        call_command('update_br_stocks_price')
        call_command('update_cripto_price')
        call_command('update_currencies_price')
        call_command('update_total_today_brl')
        call_command('update_fiis_fundamentals')
        call_command('update_br_stocks_fundamentals')
        call_command('update_stock')
        call_command('update_reit')
        call_command('update_usd_price')
        call_command('update_total_today_usd')
