
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        commands = [
            'get_historical_currency',
            'update_cripto_price', 
            'update_currencies_price', 
            'update_from_google',
            'update_from_fmp',
            'update_from_fundamentus',
            'update_from_yahoo',
            'update_total_dividends', 
            'update_total_today'
            ]

        errors = []

        for command in commands:
            try:
                call_command(command)
            except Exception as e:
                errors.append(f'Error while running {command}: {e}')

        if errors:
            print("The following errors occurred:")
            for error in errors:
                print(error)