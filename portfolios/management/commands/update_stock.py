# update stocks price
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Stocks
import requests

# This file updates the fundamentalist data for Brazilian REITs (Stock)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Stock fundmentals data...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/18rUBtnbn0x9VarS2XUL3Vxs7ZyHlHR2v_RNBNn3VssE/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        stocks = pd.read_html(r.text,  decimal=',')[0]
        stocks = stocks[['A', 'F', 'G', 'H', 'K', 'M']]
        stocks.columns = ['ticker', 'price', 'top_52w',
                          'bottom_52w', 'twelve_m_dividend', 'twelve_m_yield']
        stocks = stocks.drop([0, 1])
        stocks = stocks.dropna(subset=['ticker'])
        # remove . , from price top_52w bottom_52w
        stocks['price'] = stocks['price'].str.replace(',', '')
        stocks['top_52w'] = stocks['top_52w'].str.replace(',', '')
        stocks['bottom_52w'] = stocks['bottom_52w'].str.replace(',', '')
        stocks = stocks.set_index('ticker')

        # print(stocks)

        queryset = Stocks.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge stocks and app_df
        df = app_df.merge(stocks, left_on="ticker",
                          right_on="ticker", how='inner')
        # print(df)

        # # Update stocks

        for index, row in df.iterrows():
            try:
                stocks = Stocks.objects.get(id=row['id'])
                stocks.price = row['price']
                stocks.top_52w = row['top_52w']
                stocks.bottom_52w = row['bottom_52w']
                stocks.twelve_m_dividend = row['twelve_m_dividend']
                stocks.twelve_m_yield = row['twelve_m_yield']

                stocks.save()
            except Stocks.DoesNotExist:
                print('Stocks not found')

        print("Stock fundmentals data updated!")
