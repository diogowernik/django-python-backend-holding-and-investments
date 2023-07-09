# update trade price
import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment, PortfolioEvolution
# date '2021-03-01'
from datetime import datetime

# This file updates Trades from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Calculating Portfolio Evolution...")

        # get PortfolioInvestment
        investments = PortfolioInvestment.objects.filter(portfolio_id=2)
        investments = investments.values(
            'asset__category__id', 'total_today_brl', 'total_today_usd')
        investments = pd.DataFrame(investments)

        # sum all total today brl per category
        investments = investments.groupby('asset__category__id').agg(
            {'total_today_brl': 'sum', 'total_today_usd': 'sum'})

        print(investments)

        # create PortfolioEvolution
        for index, row in investments.iterrows():
            PortfolioEvolution.objects.create(
                portfolio_id=2,
                category_id=index,
                category_total_brl=row['total_today_brl'],
                category_total_usd=row['total_today_usd'],
                # date='2023-04-01' 
                date=datetime.today().strftime('%Y-%m-%d')
            )
