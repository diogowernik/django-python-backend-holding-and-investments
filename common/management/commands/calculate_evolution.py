# calculate_evolution.py

# Este script permite calcular a evolução do portfólio no Django.
# Executar 'python manage.py calculate_evolution all' calculará a evolução para todos os portfólios disponíveis.
# Executar 'python manage.py calculate_evolution [CÓDIGO]' (onde [CÓDIGO] é um código de portfólio, como 'D') 
# calculará a evolução apenas para o portfólio mapeado ao código especificado.


import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment, PortfolioEvolution
from datetime import datetime

class Command(BaseCommand):
    help = 'Calculate portfolio evolution for a given portfolio ID or all portfolios'

    def add_arguments(self, parser):
        # Add an argument for portfolio code or 'all'
        parser.add_argument('portfolio_code', type=str, help='Code of the portfolio to calculate evolution for, or "all"')

    def handle(self, *args, **options):
        # Mapping of codes to portfolio IDs
        portfolio_mapping = {
            'D': 2,
            'I': 4,
            'G': 7
        }

        portfolio_code = options['portfolio_code']
        
        if portfolio_code == 'all':
            portfolio_ids = PortfolioInvestment.objects.values_list('portfolio_id', flat=True).distinct()
        elif portfolio_code in portfolio_mapping:
            portfolio_ids = [portfolio_mapping[portfolio_code]]
            print(f"Calculating Portfolio Evolution for portfolio {portfolio_ids[0]} ({portfolio_code})...")
        else:
            print(f"Invalid portfolio code: {portfolio_code}")
            return

        for portfolio_id in portfolio_ids:
            # get PortfolioInvestment
            investments = PortfolioInvestment.objects.filter(portfolio_id=portfolio_id)
            investments = investments.values(
                'asset__category__id', 'total_today_brl', 'total_today_usd')
            investments = pd.DataFrame(investments)

            # sum all total today brl per category
            investments = investments.groupby('asset__category__id').agg(
                {'total_today_brl': 'sum', 'total_today_usd': 'sum'})

            print(f"Portfolio {portfolio_id} Evolution:")
            print(investments)

            # create PortfolioEvolution
            for index, row in investments.iterrows():
                PortfolioEvolution.objects.create(
                    portfolio_id=portfolio_id,
                    category_id=index,
                    category_total_brl=row['total_today_brl'],
                    category_total_usd=row['total_today_usd'],
                    date='2024-01-01'
                    # date=datetime.today().strftime('%Y-%m-%d')
                )
