# update br_stocks price
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import BrStocks
import requests

# This file updates the fundamentalist data for Brazilian Stocks (BrStocks)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating BrStocks fundmentals data...")

        # Get the data from the FundExplorer
        url = 'https://www.fundamentus.com.br/resultado.php'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        br_stocks = pd.read_html(r.text,  decimal=',')[0]
        br_stocks = br_stocks[['Papel', 'P/L', 'P/VP', 'Div.Yield',
                               'EV/EBIT', 'ROIC', 'ROE']]
        br_stocks.columns = ['ticker', 'pl', 'p_vpa', 'twelve_m_yield', 'ev_ebit',
                             'roic', 'roe']
        # br_stocks.columns = ['ticker', 'setor', 'last_dividend', 'last_yield',
        #                      'six_m_yield', 'twelve_m_yield', 'p_vpa', 'assets']
        # br_stocks['last_dividend'] = br_stocks['last_dividend'].str[3:]
        # br_stocks['last_dividend'] = br_stocks['last_dividend'].str.replace(
        #     ',', '.')
        # br_stocks['last_yield'] = br_stocks['last_yield'].str.replace(',', '.')
        # br_stocks['last_yield'] = br_stocks['last_yield'].str.replace('%', '')
        # br_stocks['six_m_yield'] = br_stocks['six_m_yield'].str.replace(
        #     ',', '.')
        # br_stocks['six_m_yield'] = br_stocks['six_m_yield'].str.replace(
        #     '%', '')
        # br_stocks['twelve_m_yield'] = br_stocks['twelve_m_yield'].str.replace(
        #     ',', '.')
        # br_stocks['twelve_m_yield'] = br_stocks['twelve_m_yield'].str.replace(
        #     '%', '')
        # br_stocks['p_vpa'] = br_stocks['p_vpa'] / 100
        # # br_stocks['setor'] = br_stocks['setor'].str.replace('Títulos e Val. Mob.', 'TVM')
        # # br_stocks['setor'] = br_stocks['setor'].str.replace(
        # #     'Lajes Corporativas', 'Lajes')
        br_stocks = br_stocks.set_index('ticker')

        # print(br_stocks)

        queryset = BrStocks.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge br_stocks and app_df
        df = app_df.merge(br_stocks, left_on="ticker",
                          right_on="ticker", how='inner')
        # fields to float and save
        df['pl'] = df['pl'].astype(float) / 100
        df['pl'] = df['pl'].round(2)
        df['p_vpa'] = df['p_vpa'].astype(float) / 100
        df['p_vpa'] = df['p_vpa'].round(2)
        df['ev_ebit'] = df['ev_ebit'].astype(float) / 100
        df['ev_ebit'] = df['ev_ebit'].round(2)

        df['twelve_m_yield'] = df['twelve_m_yield'].str.replace(
            ',', '.')
        df['twelve_m_yield'] = df['twelve_m_yield'].str.replace('%', '')
        df['twelve_m_yield'] = df['twelve_m_yield'].astype(float)
        df['roic'] = df['roic'].str.replace(',', '.')
        df['roic'] = df['roic'].str.replace('%', '')
        df['roic'] = df['roic'].astype(float)
        df['roe'] = df['roe'].str.replace(',', '.')
        df['roe'] = df['roe'].str.replace('%', '')
        df['roe'] = df['roe'].astype(float)

        # print(df)

        # Update br_stocks

        for index, row in df.iterrows():
            try:
                br_stock = BrStocks.objects.get(id=row['id'])
                br_stock.pl = row['pl']
                br_stock.p_vpa = row['p_vpa']
                br_stock.twelve_m_yield = row['twelve_m_yield']
                br_stock.ev_ebit = row['ev_ebit']
                br_stock.roic = row['roic']
                br_stock.roe = row['roe']
                br_stock.save()
            except BrStocks.DoesNotExist:
                print('BrStock not found')

        print("BrStocks fundmentals data updated!")
