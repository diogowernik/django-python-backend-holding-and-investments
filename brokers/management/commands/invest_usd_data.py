from django.core.management.base import BaseCommand
import pandas as pd
from timewarp.models import CurrencyHistoricalPrice

def usd_price(date):
    try:
        currency_price = CurrencyHistoricalPrice.objects.filter(
            currency_pair="USDBRL",
            date__lte=date
        ).latest('date')
        return currency_price.close
    except CurrencyHistoricalPrice.DoesNotExist:
        print(f"No currency price found for date {date}")
        return None

class Command(BaseCommand):
    help = 'Reads data from a CSV file, renames headers, processes data, categorizes tickers, separates it into specific events DataFrames, and prints them using Pandas'

    def handle(self, *args, **options):
        # Diretório onde o arquivo CSV está armazenado
        csv_directory = 'brokers/management/'
        csv_filename = 'complete_divest_usd_events.csv'  

        # Caminho completo do arquivo CSV
        csv_filepath = f'{csv_directory}/{csv_filename}'

        # Lendo o arquivo CSV usando Pandas
        data = pd.read_csv(csv_filepath)

        # Filtrando apenas os campos necessários
        filtered_data = data[['ticker', 'trade_date', 'price_brl', 'price_usd', 'broker_name', 'trade_amount']]

        # Salvando o DataFrame filtrado em um novo arquivo CSV
        new_csv_filepath = f'{csv_directory}/divest_usd_events.csv'
        filtered_data.to_csv(new_csv_filepath, index=False)

        # Imprimindo o DataFrame atualizado
        print(filtered_data)
