# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioTrade, PortfolioInvestment

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

        trades = trades.sort_values(by=['date'])
        # get only trades with order 'Compra'
        trades = trades[trades['order'] == 'C']

        # sum all total cost brl and all shares ammount sum tax brl and usd
        trades = trades.groupby('asset').agg(
            {'total_cost_brl': 'sum', 'total_cost_usd': 'sum', 'shares_amount': 'sum', 'tax_brl': 'sum', 'tax_usd': 'sum'})

        # average price = total cost sum + tax brl sum / shares amount sum

        trades['share_average_price_brl'] = trades['total_cost_brl'] + \
            trades['tax_brl']
        trades['share_average_price_brl'] = trades['share_average_price_brl'] / \
            trades['shares_amount']
        trades['share_average_price_brl'] = trades['share_average_price_brl'].round(
            2)

        trades['share_average_price_usd'] = trades['total_cost_usd'] + \
            trades['tax_usd']
        trades['share_average_price_usd'] = trades['share_average_price_usd'] / \
            trades['shares_amount']
        trades['share_average_price_usd'] = trades['share_average_price_usd'].round(
            2)

        # set index == asset

        # trades = trades.set_index('asset')

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
            'id', 'asset__ticker', 'share_average_price_brl', 'share_average_price_usd', 'trade_profit_brl', 'trade_profit_usd')
        investments = pd.DataFrame(investments)
        print(investments)
