# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioHistory, PortfolioInvestment

# This file updates Trades from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Calculating share average cost...")

        # get PortfolioTrade where category is 'FII' or 'ETF' or 'Ação'

        # print(investments)
        trades = PortfolioHistory.objects.filter(portfolio_id=2)

        trades = trades.values('id', 'asset', 'trade_profit_brl',
                               'trade_profit_usd')
        trades = pd.DataFrame(trades)

        # trades = trades[trades['asset'] == 'HGLG11']

        # get only trades with order 'Compra'
        # trades = trades[trades['order'] == 'C']

        # sum all total cost brl and all shares ammount sum tax brl and usd
        trades = trades.groupby('asset').agg(
            {'trade_profit_brl': 'sum', 'trade_profit_usd': 'sum'})

        # round values
        trades['trade_profit_brl'] = trades['trade_profit_brl'].round(2)
        trades['trade_profit_usd'] = trades['trade_profit_usd'].round(2)

        # set index == asset

        # trades = trades.set_index('asset')

        print(trades)

        # update PortfolioInvestment
        # find PortfolioInvestment with asset__ticker == asset
        for index, row in trades.iterrows():
            try:
                investment = PortfolioInvestment.objects.get(
                    asset__ticker=index, portfolio_id=2)
                investment.trade_profit_brl = row['trade_profit_brl']
                investment.trade_profit_usd = row['trade_profit_usd']
                # investment.trade_profit_brl = 0
                # investment.trade_profit_usd = 0
                investment.save()
                print('updated investment: ', investment.asset.ticker)
            except:
                print("Asset not found: " + index)

        # show updated PortfolioInvestment
        investments = PortfolioInvestment.objects.filter(portfolio_id=2)
        investments = investments.values(
            'id', 'asset__ticker', 'trade_profit_brl', 'trade_profit_usd')
        investments = pd.DataFrame(investments)
        print(investments)
