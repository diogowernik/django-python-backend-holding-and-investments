import yfinance as yf
from django.core.management.base import BaseCommand
from timewarp.models import CurrencyHistoricalPrice
from datetime import datetime, timedelta
import pandas as pd

def update_historical_prices(currency_pair):
    print(f'Updating {currency_pair} historical prices...')
    # Encontra a data mais recente no banco de dados
    latest_entry = CurrencyHistoricalPrice.objects.filter(currency_pair=currency_pair).order_by('-date').first()

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
        # print(f'Não há novos dados para {currency_pair}. O banco de dados já está atualizado.')
        return
    
    # Baixa os dados da taxa de câmbio
    data = yf.download(f'{currency_pair}=X', start=start_date.strftime('%Y-%m-%d'), end=datetime.today().strftime('%Y-%m-%d'))

    # Verifica se o DataFrame está vazio
    if data.empty:
        # print(f'Não há novos dados para {currency_pair}. O banco de dados já está atualizado.')
        return

    data = data.sort_index()

    # Para cada registro no DataFrame
    for date, row in data.iterrows():
        # Cria um novo CurrencyHistoricalPrice
        CurrencyHistoricalPrice.objects.create(
            currency_pair=currency_pair,
            date=date.date(),
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
        )
    
    print(f'Done')

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Moedas, euro, real, dólar
        update_historical_prices('USDBRL')
        update_historical_prices('EURBRL')

        update_historical_prices('BRLUSD')
        update_historical_prices('EURUSD')

        update_historical_prices('USDEUR')
        update_historical_prices('BRLEUR')



        
        

