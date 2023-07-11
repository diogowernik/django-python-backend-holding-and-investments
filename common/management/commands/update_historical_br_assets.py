import yfinance as yf
from django.core.management.base import BaseCommand
from investments.models import AssetHistoricalPrice, Asset
from datetime import datetime, timedelta
import pandas as pd

def update_asset_historical_prices(asset_ticker):
    print(f'Updating {asset_ticker} historical prices...')
    # Encontra a data mais recente no banco de dados
    latest_entry = AssetHistoricalPrice.objects.filter(asset__ticker=asset_ticker).order_by('-date').first()

    # Se já houver uma entrada no banco de dados, use a data da entrada mais recente como a data de início
    if latest_entry is not None:
        start_date = latest_entry.date
    else:
        # Se não houver entradas no banco de dados, use uma data de início padrão
        start_date = '2020-01-01'

    # Adicione um dia à data de início para evitar a duplicação do último dia baixado
    start_date = pd.to_datetime(start_date) + timedelta(days=1)

    # Se a data de início for depois da data de fim, o banco de dados está atualizado
    if start_date > pd.to_datetime(datetime.today().date()):
        print(f'Não há novos dados para {asset_ticker}. O banco de dados já está atualizado.')
        return

    # Modifica o ticker para incluir .SA se o ativo for brasileiro
    download_ticker = asset_ticker if asset_ticker.endswith('.SA') else asset_ticker + '.SA'
    
    # Baixa os dados do ativo
    data = yf.download(download_ticker, start=start_date.strftime('%Y-%m-%d'), end=datetime.today().strftime('%Y-%m-%d'))

    # Verifica se o DataFrame está vazio
    if data.empty:
        print(f'Não há novos dados para {asset_ticker}. O banco de dados já está atualizado.')
        return

    # head 10 for testing purposes
    # data = data.head(10)

    data = data.sort_index()
    asset = Asset.objects.get(ticker=asset_ticker)  # Obter o objeto Asset associado

    # Para cada registro no DataFrame
    for date, row in data.iterrows():
        # Cria um novo AssetHistoricalPrice
        AssetHistoricalPrice.objects.create(
            asset=asset,
            currency = 'BRL',
            date=date.date(),
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
        )

    print(f'Finished updating {asset_ticker} historical prices.')

class Command(BaseCommand):
    def handle(self, *args, **options):
        update_asset_historical_prices('HGLG11')
        update_asset_historical_prices('HGRE11')
        update_asset_historical_prices('HGBS11')
        update_asset_historical_prices('BTAL11')
        update_asset_historical_prices('KNRI11')
        update_asset_historical_prices('RZTR11')

        update_asset_historical_prices('TAEE11')


        
        

