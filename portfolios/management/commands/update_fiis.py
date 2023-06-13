# update fii price_brl
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Fii
import requests

# This file updates the fundamentalist data for Brazilian REITs (Fiis)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Fiis fundmentals data...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/1aOn6Fw_7arz-XcNB8KPIooK1Xgkg3lanRPh90PkB3O8/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        fii = pd.read_html(r.text,  decimal=',')[0]
        fii = fii[['A', 'F', 'G', 'H']]
        fii.columns = ['ticker', 'price_brl', 'top_52w',
                        'bottom_52w']
        fii = fii.drop([0, 1])
        fii = fii.dropna(subset=['ticker'])
        fii = fii.set_index('ticker')

        print(fii)

        queryset = Fii.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df = app_df.set_index('ticker')
        print(app_df)

        # Merge fii and app_df
        df = app_df.merge(fii, left_on="ticker",
                          right_on="ticker", how='inner')

        # # Update fii
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl / usd_brl_price
        df['price_usd'] = df['price_brl'].astype(float) / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        print(df)

        for index, row in df.iterrows():
            try:
                fii = Fii.objects.get(id=row['id'])
                fii.price_brl = row['price_brl']
                fii.price_usd = row['price_usd']
                fii.top_52w = row['top_52w']
                fii.bottom_52w = row['bottom_52w']

                fii.save()
            except Fii.DoesNotExist:
                print('Fii not found')

        print("Fiis price, top, bottom updated!")
