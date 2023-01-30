# update dividends price
from tokenize import group
from numpy import average
import pandas as pd
from django.core.management.base import BaseCommand
from dividends.models import Dividend
from investments.models import Asset
import requests
from portfolios.models import PortfolioInvestment, PortfolioDividend

# This file updates Dividends from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Dividends Fix...")

        # Get the data from the PortfolioDividend

        queryset = PortfolioDividend.objects.all()
        dividends = pd.DataFrame.from_records(queryset.values())
        dividends = dividends[[
            'id', 'ticker', 'category', 'subcategory'
        ]]
        dividends.columns = [
            'id', 'ticker', 'category', 'subcategory'
        ]

        # set index id
        dividends = dividends.set_index('id')

        print(dividends)

        # where category is 'FII' change to 'Fundos Imobiliários''
        # if 'Reit' to 'REITs'
        # if 'PrivateAssets' to 'Propriedades'
        # if 'Ação' to 'Ações Brasileiras'
        # if 'Ações' to 'Ações Brasileiras'
        # if 'Stock' to 'Stocks'

        for index, row in dividends.iterrows():
            if row['category'] == 'FII':
                PortfolioDividend.objects.filter(id=index).update(
                    category='Fundos Imobiliários')
            elif row['category'] == 'Reit':
                PortfolioDividend.objects.filter(id=index).update(
                    category='REITs')
            elif row['category'] == 'PrivateAsset':
                PortfolioDividend.objects.filter(id=index).update(
                    category='Propriedades')
            elif row['category'] == 'Ação':
                PortfolioDividend.objects.filter(id=index).update(
                    category='Ações Brasileiras')
            elif row['category'] == 'Ações':
                PortfolioDividend.objects.filter(id=index).update(
                    category='Ações Brasileiras')
            elif row['category'] == 'Stock':
                PortfolioDividend.objects.filter(id=index).update(
                    category='Stocks')

        # print(dividends)
