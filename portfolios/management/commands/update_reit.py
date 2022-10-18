# update reit price_brl
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Reit
import requests

# This file updates the fundamentalist data for Brazilian REITs (Reits)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Reits fundmentals data...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/16zJuluKOqz2rEqrQ2O_ijapdPsEshbBhOa-hRFn2Dl8/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        reit = pd.read_html(r.text,  decimal=',')[0]
        reit = reit[['A', 'F', 'G', 'H', 'K', 'M']]
        reit.columns = ['ticker', 'price_brl', 'top_52w',
                        'bottom_52w', 'twelve_m_dividend', 'twelve_m_yield']
        reit = reit.drop([0, 1])
        reit = reit.dropna(subset=['ticker'])
        # remove . , from price_brl top_52w bottom_52w
        reit['price_brl'] = reit['price_brl'].str.replace(',', '')
        reit['top_52w'] = reit['top_52w'].str.replace(',', '')
        reit['bottom_52w'] = reit['bottom_52w'].str.replace(',', '')
        reit = reit.set_index('ticker')

        # print(reit)

        # # print(reit)

        queryset = Reit.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge reit and app_df
        df = app_df.merge(reit, left_on="ticker",
                          right_on="ticker", how='inner')

        # # Update reit
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl / usd_brl_price
        df['price_usd'] = df['price_brl'].astype(float) / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        # print('df')
        print(df)

        for index, row in df.iterrows():
            try:
                reit = Reit.objects.get(id=row['id'])
                reit.price_brl = row['price_brl']
                reit.price_usd = row['price_usd']
                reit.top_52w = row['top_52w']
                reit.bottom_52w = row['bottom_52w']
                reit.twelve_m_dividend = row['twelve_m_dividend']
                reit.twelve_m_yield = row['twelve_m_yield']

                reit.save()
            except Reit.DoesNotExist:
                print('Reit not found')

        print("Reits fundmentals data updated!")
