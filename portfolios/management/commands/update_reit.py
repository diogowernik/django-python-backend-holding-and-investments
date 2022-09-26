# update reit price
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
        reit.columns = ['ticker', 'price', 'top_52w',
                        'bottom_52w', 'twelve_m_dividend', 'twelve_m_yield']
        reit = reit.drop([0, 1])
        reit = reit.dropna(subset=['ticker'])
        # remove . , from price top_52w bottom_52w
        reit['price'] = reit['price'].str.replace(',', '')
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
        # print(df)

        # # Update reit

        for index, row in df.iterrows():
            try:
                reit = Reit.objects.get(id=row['id'])
                reit.price = row['price']
                reit.top_52w = row['top_52w']
                reit.bottom_52w = row['bottom_52w']
                reit.twelve_m_dividend = row['twelve_m_dividend']
                reit.twelve_m_yield = row['twelve_m_yield']

                reit.save()
            except Reit.DoesNotExist:
                print('Reit not found')

        print("Reits fundmentals data updated!")

        # queryset = Reit.objects.values_list(
        #     "id", "ticker", "twelve_m_yield", "p_vpa",
        #     # "six_m_yield", "last_yield"
        # )
        # ranking_df = pd.DataFrame(list(queryset), columns=[
        #                           "id", "ticker", "twelve_m_yield", "p_vpa"])
        # ranking_df = ranking_df.set_index('ticker')
        # # tweleve_m_yield higher to lower
        # ranking_df['twelve_m_yield'] = pd.to_numeric(
        #     ranking_df['twelve_m_yield'])
        # ranking_df['ranking_twelve_m_yield'] = ranking_df['twelve_m_yield'].rank(
        #     ascending=False, method='first')
        # # ranking_df = ranking_df.sort_values(by=['ranking_twelve_m_yield'])

        # # six_m_yield higher to lower
        # # ranking_df['six_m_yield'] = pd.to_numeric(
        # #     ranking_df['six_m_yield'])
        # # ranking_df['ranking_six_m_yield'] = ranking_df['six_m_yield'].rank(
        # #     ascending=False, method='first')
        # # ranking_df = ranking_df.sort_values(by=['ranking_six_m_yield'])

        # # last_yield higher to lower
        # # ranking_df['last_yield'] = pd.to_numeric(
        # #     ranking_df['last_yield'])
        # # ranking_df['ranking_last_yield'] = ranking_df['last_yield'].rank(
        # #     ascending=False, method='first')
        # # ranking_df = ranking_df.sort_values(by=['ranking_last_yield'])

        # # p_vpa lower to higher
        # ranking_df['p_vpa'] = pd.to_numeric(ranking_df['p_vpa'])
        # ranking_df['ranking_p_vpa'] = ranking_df['p_vpa'].rank(
        #     ascending=True, method='first')
        # # ranking_df = ranking_df.sort_values(by=['ranking_p_vpa'])

        # # sum ranking_twelve_m_yield and ranking_p_vpa
        # ranking_df['ranking'] = ranking_df['ranking_twelve_m_yield'] + \
        #     ranking_df['ranking_p_vpa']
        # ranking_df = ranking_df.sort_values(by=['ranking'])

        # for index, row in ranking_df.iterrows():
        #     try:
        #         reit = Reit.objects.get(id=row['id'])
        #         reit.ranking = row['ranking']

        #         reit.save()
        #     except Reit.DoesNotExist:
        #         print('Reit not found')

        # print("Reits ranking updated!")

        # # print(df)
