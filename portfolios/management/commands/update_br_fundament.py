# update assets price_brl
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset
import requests

# This file updates the fundamentalist data for Brazilian REITs (Asset)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Br fundmentals data...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/1-RnGncfUTlyYMSZZ6CHbLZtPLLhdKG8sGPNFeopbeHs/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        assets = pd.read_html(r.text,  decimal=',')[0]
        assets = assets[['A', 'F', 'G', 'H']]
        assets.columns = ['ticker', 'price_brl', 'top_52w',
                          'bottom_52w']
        assets = assets.drop([0, 1])
        assets = assets.dropna(subset=['ticker'])
        # remove . , from price_brl top_52w bottom_52w
        assets['price_brl'] = assets['price_brl'].str.replace(',', '')
        assets['top_52w'] = assets['top_52w'].str.replace(',', '')
        assets['bottom_52w'] = assets['bottom_52w'].str.replace(',', '')
        assets = assets.set_index('ticker')

        # print(assets)

        queryset = Asset.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge assets and app_df
        df = app_df.merge(assets, left_on="ticker",
                          right_on="ticker", how='inner')
        # print(df)
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl / usd_brl_price
        df['price_usd'] = df['price_brl'].astype(float) / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        # print('df')
        # print(df)

        # # Update assets

        for index, row in df.iterrows():
            try:
                assets = Asset.objects.get(id=row['id'])
                assets.price_brl = row['price_brl']
                assets.price_usd = row['price_usd']
                assets.top_52w = row['top_52w']
                assets.bottom_52w = row['bottom_52w']

                assets.save()
            except Asset.DoesNotExist:
                print('Asset not found')

        print("Done")
