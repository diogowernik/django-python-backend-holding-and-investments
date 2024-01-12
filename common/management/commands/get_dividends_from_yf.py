from django.core.management.base import BaseCommand
from investments.models import Asset
from timewarp.models import CurrencyHistoricalPrice
from dividends.models import Dividend
import yfinance as yf
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Lista de tickers para atualizar
        tickers = ['HGLG11', 'BRCO11', 'KNRI11', 'HGRE11', 'HGBS11', 'HGCR11']
        for ticker in tickers:
            self.update_asset_dividends(f'{ticker}.SA')

    def update_asset_dividends(self, ticker):
        print(f'Updating {ticker} dividends...')
        fundo = yf.Ticker(ticker)
        dividendos = fundo.dividends

        if dividendos.empty:
            print(f'Nenhum dividendo encontrado para {ticker}.')
            return

        df = dividendos.reset_index()
        df.columns = ['pay_date', 'value_per_share_brl']
        df['asset'] = ticker.replace('.SA', '')

        # Filtrar para dividendos a partir de 2022
        start_year = 2022
        df = df[df['pay_date'].dt.year >= start_year]

        # Ajuste das datas
        df['record_date'] = df['pay_date'] - pd.offsets.MonthEnd(1)
        df['pay_date'] = df['pay_date'].apply(lambda x: x.replace(day=15))

        for _, row in df.iterrows():
            asset = Asset.objects.get(ticker=row['asset'])
            usdbrl_rate = self.get_currency_historical_price('USDBRL', row['pay_date'])
            value_per_share_usd = row['value_per_share_brl'] / usdbrl_rate

            Dividend.objects.update_or_create(
                asset=asset,
                record_date=row['record_date'],
                defaults={
                    'value_per_share_brl': row['value_per_share_brl'],
                    'value_per_share_usd': value_per_share_usd,
                    'pay_date': row['pay_date']
                }
            )
        print(f'Finished updating {ticker} dividends.')

    def get_currency_historical_price(self, currency_pair, date):
        try:
            return CurrencyHistoricalPrice.objects.get(currency_pair=currency_pair, date=date).close
        except CurrencyHistoricalPrice.DoesNotExist:
            return CurrencyHistoricalPrice.objects.filter(currency_pair=currency_pair, date__lt=date).order_by('-date').first().close
