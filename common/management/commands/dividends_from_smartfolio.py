# update dividends price
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from portfolios.models import PortfolioDividend

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Dividends from Meus Dividendos...")

        # Get the data from google sheet
        url = 'https://docs.google.com/spreadsheets/d/1jV3rxkIJxcg-GU9H0tN6Pao-bzzOJxLdtlmJN_ztSIQ/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        dividends = pd.read_html(r.text,  decimal='.', thousands=',')[0]
        dividends = dividends[[
            'B', 'C', 'D', 'F',
            'G', 'I','J', 'K', 
            'L','M']]
        dividends.columns = [
            'record_date', 'pay_date', 'category', 'subcategory', 
            'ticker',  'value_per_share', 'average_price', 'yield',
            'shares_amount', 'total_dividend']

        dividends = dividends.drop([0, 1])
        dividends = dividends.dropna(subset=['ticker'])
        # set index
        dividends = dividends.set_index('ticker')

        # remove first 3 caracters from total_dividend and change ,  to .
        dividends['total_dividend'] = dividends['total_dividend'].str[3:]
        dividends['total_dividend'] = dividends['total_dividend'].str.replace(',', '.')

        # if ticker = Ativo drop row
        dividends = dividends[dividends.index != 'Ativo']

        # record date and pay date to datetime ex: from 15/02/2023 to 2023-02-15
        dividends['record_date'] = pd.to_datetime(
            dividends['record_date'], format='%d/%m/%Y')
        dividends['pay_date'] = pd.to_datetime(
            dividends['pay_date'], format='%d/%m/%Y')
        
        # average_price to float
        dividends['average_price'] = dividends['average_price'].astype(float)

        # value_per_share to float
        dividends['value_per_share'] = dividends['value_per_share'].astype(float)

        # total_dividend to float
        dividends['total_dividend'] = dividends['total_dividend'].astype(float)

        # FII to Fundo Imobiliário
        dividends['subcategory'] = dividends['subcategory'].str.replace('FII', 'Fundos Imobiliários')

        # FI-Infra to Fundo Imobiliário
        dividends['subcategory'] = dividends['subcategory'].str.replace('FI-Infra', 'Fundos Imobiliários')

        # Ação to Ações Brasileiras
        dividends['subcategory'] = dividends['subcategory'].str.replace('Ação', 'Ações Brasileiras')

        # Stock to Stocks
        dividends['subcategory'] = dividends['subcategory'].str.replace('Stock', 'Stocks')

        # REIT to REITs
        dividends['subcategory'] = dividends['subcategory'].str.replace('REIT', 'REITs')

        # print(dividends)

        usd_dividends = dividends[dividends['category'] == 'Internacional']

        print(usd_dividends)

        brl_dividends = dividends[dividends['category'] != 'Internacional']

        print(brl_dividends)

        # get usd price today
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]
        
    # for each brl_dividends
        for index, row in brl_dividends.iterrows():
            try:
                # create PortfolioDividend
                PortfolioDividend.objects.create(
                    # Find Asset by ticker
                    portfolio_id=2,
                    ticker=index,
                    category=row['subcategory'],
                    record_date=row['record_date'],
                    pay_date=row['pay_date'],
                    shares_amount=row['shares_amount'],
                    average_price_brl=row['average_price'],
                    average_price_usd=round(row['average_price']/usd_brl_price, 2),
                    value_per_share_brl=row['value_per_share'],
                    total_dividend_brl=row['total_dividend'],
                    usd_on_pay_date=usd_brl_price,
                    value_per_share_usd=round(row['value_per_share']/usd_brl_price, 2),
                    total_dividend_usd=round(row['total_dividend']/usd_brl_price, 2),
                )
            except Exception as e:
                print(e)
                pass
    
    # for each usd_dividends
        for index, row in usd_dividends.iterrows():
            try:
                # create PortfolioDividend
                PortfolioDividend.objects.create(
                    # Find Asset by ticker
                    portfolio_id=2,
                    ticker=index,
                    category=row['subcategory'],
                    record_date=row['record_date'],
                    pay_date=row['pay_date'],
                    shares_amount=row['shares_amount'],
                    average_price_brl=round(row['average_price']*usd_brl_price, 2),
                    average_price_usd=row['average_price'],
                    value_per_share_brl=round(row['value_per_share']*usd_brl_price, 2),
                    total_dividend_brl=round(row['total_dividend']*usd_brl_price, 2),
                    usd_on_pay_date=usd_brl_price,
                    value_per_share_usd=row['value_per_share'],
                    total_dividend_usd=row['total_dividend'],
                )
            except Exception as e:
                print(e)
                pass
        



        print("Dividendo Updated!")
