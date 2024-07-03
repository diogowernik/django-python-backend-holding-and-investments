from django.core.management.base import BaseCommand
import pandas as pd
from django.utils import timezone
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
    help = 'Creates a CSV file for SendMoneyEvent model with sample data'

    def handle(self, *args, **options):
        # Diretório onde o arquivo CSV será armazenado
        csv_directory = 'brokers/management/'
        csv_filename = 'send_money_events.csv'

        # Valores dos depósitos por ano
        investments_by_year_usd = {
            2019: 238.27,
            2020: 1284.80,
            2021: 130.36,
            2022: 21629.72,
            2023: 14535.73,
            2024: 1525.84
        }

        # Dados das transferências
        transfer_data = []
        for year, amount in investments_by_year_usd.items():
            transfer_date = f'{year}-01-18'
            exchange_rate = usd_price(transfer_date)
            if exchange_rate is None:
                print(f"Skipping transfer for {year} due to missing exchange rate.")
                continue
            from_transfer_amount_brl = amount * exchange_rate
            transfer_data.append({
                'from_broker_name': 'Itaú',
                'to_broker_name': 'Charles Schwab',
                'from_transfer_amount': from_transfer_amount_brl,
                'exchange_rate': exchange_rate,
                'transfer_date': transfer_date
            })

        # Convertendo os dados para um DataFrame do Pandas
        df = pd.DataFrame(transfer_data)

        # Caminho completo do arquivo CSV
        csv_filepath = f'{csv_directory}/{csv_filename}'

        # Salvando o DataFrame em um arquivo CSV
        df.to_csv(csv_filepath, index=False)

        # Imprimindo o DataFrame atualizado
        print(df)
