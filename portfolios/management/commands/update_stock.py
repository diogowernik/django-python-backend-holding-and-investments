# update stocks price_brl
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
        stocks.columns = ['ticker', 'price_brl', 'top_52w',
                          'bottom_52w', 'twelve_m_dividend', 'twelve_m_yield']
        stocks = stocks.drop([0, 1])
        stocks = stocks.dropna(subset=['ticker'])
        # remove . , from price_brl top_52w bottom_52w
        stocks['price_brl'] = stocks['price_brl'].str.replace(',', '')
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
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl / usd_brl_price
        df['price_usd'] = df['price_brl'].astype(float) / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        # print('df')
        print(df)

        # # Update stocks

        for index, row in df.iterrows():
            try:
                stocks = Stocks.objects.get(id=row['id'])
                stocks.price_brl = row['price_brl']
                stocks.price_usd = row['price_usd']
                stocks.top_52w = row['top_52w']
                stocks.bottom_52w = row['bottom_52w']
                stocks.twelve_m_dividend = row['twelve_m_dividend']
                stocks.twelve_m_yield = row['twelve_m_yield']

                stocks.save()
            except Stocks.DoesNotExist:
                print('Stocks not found')

        print("Stock fundmentals data updated!")
