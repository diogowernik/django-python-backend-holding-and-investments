
from django.core.management.base import BaseCommand
from django.core.management import call_command
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investments.settings")
# django.setup()


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            call_command('update_fiis_price')
        except Exception as e:
            print(e)
        try:
            call_command('update_br_stocks_price')
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
            call_command('update_total_today')
        except Exception as e:
            print(e)
        try:
            call_command('update_fiis_fundamentals')
        except Exception as e:
            print(e)
        try:
            call_command('update_br_stocks_fundamentals')
        except Exception as e:
            print(e)
        try:
            call_command('update_stock')
        except Exception as e:
            print(e)
        try:
            call_command('update_reit')
        except Exception as e:
            print(e)
        # try:
        #     call_command('update_usd_price')
        # except Exception as e:
        #     print(e)
        # try:
        #     call_command('update_total_today_usd')
        # except Exception as e:
        #     print(e)
