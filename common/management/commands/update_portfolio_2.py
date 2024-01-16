
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        commands = [
            'get_dividends_from_yf',
            'get_historical_currency',
            'get_historical_br_assets',
            'update_portfolio_2_fiis_evolution',
            'update_portfolio_2_dividends',
        ]


        errors = []

        for command in commands:
            try:
                call_command(command)
            except Exception as e:
                errors.append(f'Error while running {command}: {e}')

        # Tente chamar calculate_evolution com o argumento 'I' de forma diferente
        try:
            call_command('calculate_evolution', 'I')
        except Exception as e:
            errors.append(f'Error while running calculate_evolution with I: {e}')

        if errors:
            print("The following errors occurred:")
            for error in errors:
                print(error)