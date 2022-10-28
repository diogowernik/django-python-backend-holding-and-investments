# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioTrade, PortfolioHistory

# This file updates Trades from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Calculating share average cost...")

        # get PortfolioTrade where category is 'FII' or 'ETF' or 'Ação'

        # print(investments)
        trades = PortfolioTrade.objects.filter(
            category__in=['FII', 'Ação'], portfolio_id=2)

        trades = trades.values('id', 'asset', 'share_cost_brl',
                               'share_cost_usd', 'total_cost_brl', 'total_cost_usd', 'order',
                               'tax_brl', 'tax_usd', 'shares_amount', 'portfolio', 'date')
        trades = pd.DataFrame(trades)

        # trades = trades[trades['asset'] == 'HGLG11']
        # only first 30 rows
        # trades = trades.head(30)

        trades = trades.sort_values(by=['date'])
        # get only trades with order 'Compra'
        # trades = trades[trades['order'] == 'C']

        print(trades)

        for index, row in trades.iterrows():

            PortfolioHistory.objects.create(
                trade_id=row['id'],
                asset=row['asset'],
                portfolio_id=row['portfolio'],

            )

        print("Done!")
