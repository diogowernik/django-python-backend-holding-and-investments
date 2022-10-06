# update dividends price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
from dividends.models import Dividend
from investments.models import Asset
import requests
from portfolios.models import PortfolioAsset, PortfolioDividend

# This file updates Dividends from Degiro


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Dividends from Meus Dividendos...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/1jV3rxkIJxcg-GU9H0tN6Pao-bzzOJxLdtlmJN_ztSIQ/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        dividends = pd.read_html(r.text,  decimal='.', thousands=',')[0]
        dividends = dividends[['A', 'B', 'C',
                               'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O']]
        dividends.columns = ['ticker', 'category', 'subcategory', 'record_date', 'pay_date', 'shares_amount',
                             'value_per_share_brl', 'total_dividend_brl', 'average_price_brl', 'yield_on_cost',
                             'usd_on_pay_date', 'value_per_share_usd', 'total_dividend_usd', 'average_price_usd']
        dividends = dividends.drop([0, 1])
        dividends = dividends.dropna(subset=['ticker'])
        # set index
        dividends = dividends.set_index('ticker')

        print(dividends)

        # for each dividends
        for index, row in dividends.iterrows():
            try:
                # create PortfolioDividend
                PortfolioDividend.objects.create(
                    # Find Asset by ticker
                    portfolio_id=2,
                    ticker=index,
                    category=row['category'],
                    subcategory=row['subcategory'],
                    record_date=row['record_date'],
                    pay_date=row['pay_date'],
                    shares_amount=row['shares_amount'],
                    value_per_share_brl=row['value_per_share_brl'],
                    total_dividend_brl=row['total_dividend_brl'],
                    average_price_brl=row['average_price_brl'],
                    yield_on_cost=row['yield_on_cost'],
                    usd_on_pay_date=row['usd_on_pay_date'],
                    value_per_share_usd=row['value_per_share_usd'],
                    total_dividend_usd=row['total_dividend_usd'],
                    average_price_usd=row['average_price_usd'],

                )
            except Exception as e:
                print(e)
                pass

        print("Done!")
