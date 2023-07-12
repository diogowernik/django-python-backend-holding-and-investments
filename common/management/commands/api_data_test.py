from django.core.management.base import BaseCommand
from investments.models import Asset
from brokers.models import CurrencyHistoricalPrice
from dividends.models import Dividend
import requests
import pandas as pd
from datetime import datetime

# data fetcher
def fetch_data(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    }
    r = requests.get(url, headers=header)
    return pd.read_html(r.text, decimal=',')[0]

def get_currency_historical_price(currency_pair, date):
    # Primeiro, tentamos obter o preço histórico para a data solicitada
    try:
        return CurrencyHistoricalPrice.objects.get(currency_pair=currency_pair, date=date).close
    except CurrencyHistoricalPrice.DoesNotExist:
        # Se não existir, buscamos o mais recente anterior à data solicitada
        return CurrencyHistoricalPrice.objects.filter(currency_pair=currency_pair, date__lt=date).order_by('-date').first().close


def update_asset_dividends(asset_ticker):
    print(f'Updating {asset_ticker} dividends...')
    
    url = f'https://statusinvest.com.br/fundos-imobiliarios/{asset_ticker}'
    
    asset = Asset.objects.get(ticker=asset_ticker)  # Obter o objeto Asset associado

    data = fetch_data(url)
    
    for _, row in data.iterrows():
        record_date = pd.to_datetime(row['DATA COM'], dayfirst=True)
        pay_date = pd.to_datetime(row['Pagamento'], dayfirst=True)

        # Encontra a entrada mais recente no banco de dados para esta data de registro
        # Encontra a entrada mais recente no banco de dados para esta data de registro, ativo e valor
        value_per_share_brl=row['Valor'] / 100000000

        latest_entry = Dividend.objects.filter(
            asset=asset, 
            record_date=record_date,
            value_per_share_brl=value_per_share_brl
        ).first()

        # Se já houver uma entrada no banco de dados para esta data de registro, pule esta iteração
        if latest_entry is not None:
            continue

        if record_date > datetime.now() or pay_date > datetime.now():
            continue

        # dentro do loop for em update_asset_dividends

        usdbrl_rate = get_currency_historical_price('USDBRL', pay_date)
        value_per_share_usd = row['Valor'] / 100000000 / usdbrl_rate  # Converte para a escala correta e para USD

        # Na criação do Dividend
        Dividend.objects.create(
            asset=asset,
            value_per_share_brl=row['Valor'] / 100000000,  # Converte para a escala correta
            value_per_share_usd=value_per_share_usd,
            record_date=record_date,
            pay_date=pay_date
        )

    print(f'Finished updating {asset_ticker} dividends.')

class Command(BaseCommand):
    def handle(self, *args, **options):
        update_asset_dividends('HGLG11')
        # Você pode adicionar mais chamadas update_asset_dividends aqui para outros ativos


        
        

