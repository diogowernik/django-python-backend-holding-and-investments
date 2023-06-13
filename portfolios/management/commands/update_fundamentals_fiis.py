# update fiis price
import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Fii
import requests

# This file updates the fundamentalist data for Brazilian REITs (Fiis)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Fiis fundmentals data...")

        # Get the data 
        # url = 'https://www.fundsexplorer.com.br/ranking' table vazia (antes funcionava.)
        # url = 'https://fiis.com.br/lupa-de-fiis/' 
        # url = 'https://www.clubefii.com.br/fundo_imobiliario_lista'
        # url = 'https://www.infomoney.com.br/ferramentas/comparador-de-fiis/' 
        url = 'https://www.fundamentus.com.br/fii_resultado.php'

        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        fiis = pd.read_html(r.text,  decimal=',')[0]

        print(fiis)
        # fiis = fiis[['Papel', 'Segmento', 'FFO Yield', 'Dividend Yield',
        #             'DY (6M)Acumulado', 'DY (12M)Acumulado', 'P/VPA', 'QuantidadeAtivos']]
        # fiis = fiis[['Ticker']]
        # print(fiis)
        # fiis.columns = ['ticker', 'setor', 'last_dividend', 'last_yield',
        #                 'six_m_yield', 'twelve_m_yield', 'p_vpa', 'assets']
        # fiis['last_dividend'] = fiis['last_dividend'].str[3:]
        # fiis['last_dividend'] = fiis['last_dividend'].str.replace(',', '.')
        # fiis['last_yield'] = fiis['last_yield'].str.replace(',', '.')
        # fiis['last_yield'] = fiis['last_yield'].str.replace('%', '')
        # fiis['six_m_yield'] = fiis['six_m_yield'].str.replace(',', '.')
        # fiis['six_m_yield'] = fiis['six_m_yield'].str.replace('%', '')
        # fiis['twelve_m_yield'] = fiis['twelve_m_yield'].str.replace(',', '.')
        # fiis['twelve_m_yield'] = fiis['twelve_m_yield'].str.replace('%', '')
        # fiis['p_vpa'] = fiis['p_vpa'] / 100
        # # fiis['setor'] = fiis['setor'].str.replace('Títulos e Val. Mob.', 'TVM')
        # # fiis['setor'] = fiis['setor'].str.replace(
        # #     'Lajes Corporativas', 'Lajes')
        # fiis = fiis.set_index('ticker')

        # # print(fiis)

        # queryset = Fii.objects.values_list("id", "ticker")
        # app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        # app_df = app_df.set_index('ticker')
        # # print(app_df)

        # # Merge fiis and app_df
        # df = app_df.merge(fiis, left_on="ticker",
        #                   right_on="ticker", how='inner')
        # # print(df)

        # # Update fiis

        # for index, row in df.iterrows():
        #     try:
        #         fii = Fii.objects.get(id=row['id'])
        #         fii.last_dividend = row['last_dividend']
        #         fii.last_yield = row['last_yield']
        #         fii.six_m_yield = row['six_m_yield']
        #         fii.twelve_m_yield = row['twelve_m_yield']
        #         fii.p_vpa = row['p_vpa']
        #         fii.assets = row['assets']
        #         fii.save()
        #     except Fii.DoesNotExist:
        #         print('Fii not found')

        # print("Fiis fundmentals data updated!")

        # queryset = Fii.objects.values_list(
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
        #         fii = Fii.objects.get(id=row['id'])
        #         fii.ranking = row['ranking']

        #         fii.save()
        #     except Fii.DoesNotExist:
        #         print('Fii not found')

        # print("Fiis ranking updated!")

        # # print(df)
