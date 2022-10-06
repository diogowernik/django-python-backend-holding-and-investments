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
        print("Updating Dividends from Degiro...")

        # Get the data from the FundExplorer
        url = 'https://docs.google.com/spreadsheets/d/1pnO_Pp2C0BEkQK_TDNq7aZ4Pn2FuS10uCGoR_H7OQ8U/edit?usp=sharing'
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)

        dividends = pd.read_html(r.text,  decimal=',')[0]
        dividends = dividends[['A', 'D', 'G', 'I', 'J']]
        dividends.columns = ['ticker', 'group',
                             'pay_date', 'record_date', 'updated']
        dividends = dividends.drop([0, 1])
        dividends = dividends.dropna(subset=['ticker'])
        # set index
        dividends = dividends.set_index('ticker')

        dividends['group'] = dividends['group'].str.replace(' shares', '')
        dividends['value_per_share_usd'] = dividends['group']
        dividends['value_per_share_usd'] = dividends['value_per_share_usd'].str.replace(
            'Dividend ', '')
        dividends['value_per_share_usd'] = dividends['value_per_share_usd'].str.replace(
            'Tax -', '')
        dividends['value_per_share_usd'] = dividends['value_per_share_usd'].str[:-7]
        dividends['value_per_share_usd'] = dividends['value_per_share_usd'].str.replace(
            '*', '')
        dividends['value_per_share_usd'] = dividends['value_per_share_usd'].str.replace(
            ' ', '').astype(float)

        dividends['pay_date'] = pd.to_datetime(dividends['pay_date'])
        dividends['pay_date'] = dividends['pay_date'].dt.strftime('%Y-%m-%d')
        # record_date
        dividends['record_date'] = pd.to_datetime(dividends['record_date'])
        dividends['record_date'] = dividends['record_date'].dt.strftime(
            '%Y-%m-%d')
        # updated
        # drop lines with value = true
        dividends = dividends[dividends.updated != 'VERDADEIRO']

        dividends['group'] = dividends['group'].str.replace('[0-9]', '')
        dividends['group'] = dividends['group'].str.replace('.', '')
        dividends['group'] = dividends['group'].str.replace('-', '')
        dividends['group'] = dividends['group'].str.replace(' ', '')
        dividends['group'] = dividends['group'].str.replace('*', '')

        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        print(dividends)

        # for each dividends create Dividend
        for index, row in dividends.iterrows():
            try:
                Dividend.objects.create(
                    # Find Asset by ticker
                    asset=Asset.objects.get(ticker=index),
                    value_per_share_usd=row['value_per_share_usd'],
                    value_per_share_brl=row['value_per_share_usd'] * \
                    usd_brl_price,
                    group=row['group'],
                    pay_date=row['pay_date'],
                    record_date=row['record_date'],
                )
                dividend = Dividend.objects.last()
            except Exception as e:
                print(e)
                pass
            try:
                # create PortfolioDividend
                portfolio_asset = PortfolioAsset.objects.get(
                    asset=Asset.objects.get(ticker=index))
                PortfolioDividend.objects.create(
                    # Find Asset by ticker
                    portfolio_asset=portfolio_asset,
                    dividend=dividend,
                    portfolio_id=2,
                )
            except Exception as e:
                print(e)
                pass
