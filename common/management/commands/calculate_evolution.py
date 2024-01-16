import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment, PortfolioEvolution
from datetime import datetime

class Command(BaseCommand):
    help = 'Calculate portfolio evolution for a given portfolio ID or all portfolios'

    def add_arguments(self, parser):
        parser.add_argument('portfolio_code', type=str, help='Code of the portfolio to calculate evolution for, or "all"')

    def handle(self, *args, **options):
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
        else:
            print(f"Invalid portfolio code: {portfolio_code}")
            return

        current_date = datetime.now().date().replace(day=1)

        for portfolio_id in portfolio_ids:
            investments = PortfolioInvestment.objects.filter(portfolio_id=portfolio_id)
            investments = investments.values('asset__category__id', 'total_today_brl', 'total_today_usd')
            investments = pd.DataFrame(investments)
            investments = investments.groupby('asset__category__id').agg({'total_today_brl': 'sum', 'total_today_usd': 'sum'})

            for index, row in investments.iterrows():
                # Check if a record already exists for the current month
                if not PortfolioEvolution.objects.filter(portfolio_id=portfolio_id, category_id=index, date=current_date).exists():
                    PortfolioEvolution.objects.create(
                        portfolio_id=portfolio_id,
                        category_id=index,
                        category_total_brl=row['total_today_brl'],
                        category_total_usd=row['total_today_usd'],
                        date=current_date
                    )
                    print(f"Created new record for portfolio {portfolio_id}, category {index}, date {current_date}")
        
        print("Calculation complete.")
