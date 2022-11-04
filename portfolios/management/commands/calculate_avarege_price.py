# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioTrade, PortfolioInvestment, PortfolioHistory

# This file updates Trades from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Calculating share average cost...")

        # get PortfolioTrade where category is 'FII' or 'ETF' or 'Ação'

        # print(investments)
        trades = PortfolioHistory.objects.filter(portfolio_id=2)

        trades = trades.values(
            'id', 'asset', 'share_average_price_brl', 'share_average_price_usd')
        trades = pd.DataFrame(trades)

        # get the last trade for each asset
        trades = trades.groupby('asset').last()

        print(trades)

        # update PortfolioInvestment
        # find PortfolioInvestment with asset__ticker == asset
        # update share_average_price_brl and share_average_price_usd
        for index, row in trades.iterrows():
            try:
                investment = PortfolioInvestment.objects.get(
                    asset__ticker=index, portfolio_id=2)
                investment.share_average_price_brl = row['share_average_price_brl']
                investment.share_average_price_usd = row['share_average_price_usd']
                # investment.trade_profit_brl = 0
                # investment.trade_profit_usd = 0
                investment.save()
                print('updated investment: ', investment.asset.ticker)
            except:
                print("Asset not found: " + index)

        # show updated PortfolioInvestment
        investments = PortfolioInvestment.objects.filter(portfolio_id=2)
        investments = investments.values(
            'id', 'asset__ticker', 'share_average_price_brl', 'share_average_price_usd')
        investments = pd.DataFrame(investments)
        print(investments)
