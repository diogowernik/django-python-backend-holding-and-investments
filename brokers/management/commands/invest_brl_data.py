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
        csv_filename = 'divest_brl_events.csv'  

        # Caminho completo do arquivo CSV
        csv_filepath = f'{csv_directory}/{csv_filename}'

        # Lendo o arquivo CSV usando Pandas
        data = pd.read_csv(csv_filepath)

        # Adicionando a coluna 'usd_on_date'
        data['usd_on_date'] = data['trade_date'].apply(usd_price)

        # Arrendondando para 2 casas decimais
        data['usd_on_date'] = data['usd_on_date'].round(2)

        # Calculando o preço em USD com base no preço em BRL e no valor da moeda na data
        data['price_usd'] = data.apply(lambda row: row['price_brl'] / row['usd_on_date'] if row['usd_on_date'] else None, axis=1)

        # Arredondando para 2 casas decimais
        data['price_usd'] = data['price_usd'].round(2)

        # Salvando o DataFrame atualizado em um novo arquivo CSV
        complete_csv_filepath = f'{csv_directory}/complete_divest_brl_events.csv'
        data.to_csv(complete_csv_filepath, index=False)

        # Imprimindo o DataFrame atualizado
        print(data)

