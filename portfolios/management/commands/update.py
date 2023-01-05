
from django.core.management.base import BaseCommand
from django.core.management import call_command
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investments.settings")
# django.setup()


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            call_command('update_prices')
        except Exception as e:
            print(e)
        try:
            call_command('update_cripto_price')
        except Exception as e:
            print(e)
        try:
            call_command('update_currencies_price')
        except Exception as e:
            print(e)
        try:
            call_command('update_fundamentals_br_stocks')
        except Exception as e:
            print(e)
        try:
            call_command('update_fundamentals_fiis')
        except Exception as e:
            print(e)
        try:
            call_command('update_reit')
        except Exception as e:
            print(e)
        try:
            call_command('update_stock')
        except Exception as e:
            print(e)
        try:
            call_command('update_total_dividends')
        except Exception as e:
            print(e)
        try:
            call_command('update_total_today')
        except Exception as e:
            print(e)
