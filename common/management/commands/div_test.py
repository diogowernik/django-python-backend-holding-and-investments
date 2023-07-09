# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioInvestment
from cashflow.models import AssetAveragePrice, AssetTransaction

# This file updates Trades from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.asset=1
        self.record_date = '2023-06-01 00:00:00'
        
        portfolio_investments_by_asset = PortfolioInvestment.objects.filter(asset=self.asset).values('broker', 'portfolio').distinct()
        print(portfolio_investments_by_asset)

        for portfolio_investment in portfolio_investments_by_asset:
            portfolio_investment_obj = PortfolioInvestment.objects.get(broker=portfolio_investment['broker'], portfolio=portfolio_investment['portfolio'], asset=self.asset)

            # filtre as transações do ativo pela data de registro (record_date)
            # assets_transactions = AssetAveragePrice.objects.filter(portfolio_investment=portfolio_investment_obj)
            assets_transactions = AssetTransaction.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date)
            asset_average_price = AssetAveragePrice.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date).order_by('-transaction_date').first()
            print(assets_transactions)
            print(asset_average_price)