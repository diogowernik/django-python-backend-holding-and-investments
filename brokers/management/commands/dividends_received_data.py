from django.core.management.base import BaseCommand
import pandas as pd
from datetime import timedelta

class Command(BaseCommand):
    help = 'Reads data from CSV files, filters, merges, processes, and saves them using Pandas'

    def handle(self, *args, **options):
        # Diretório onde os arquivos CSV estão armazenados
        csv_directory = 'brokers/management/'

        # Nomes dos arquivos CSV
        historical_dividends_file = 'dividends_br_until_12_2008.csv'
        recent_dividends_file = 'dividends_2019_2024.csv'  

        # Caminho completo dos arquivos CSV
        historical_filepath = f'{csv_directory}/{historical_dividends_file}'
        recent_filepath = f'{csv_directory}/{recent_dividends_file}'

        # Lendo os arquivos CSV usando Pandas
        historical_dividends = pd.read_csv(historical_filepath)
        recent_dividends = pd.read_csv(recent_filepath)

        # Filtrando as colunas do historical_dividends
        historical_dividends_filtered = historical_dividends[['asset_ticker', 'value_per_share_brl', 'record_date', 'pay_date']]

        # Criando DataFrames separados com base na categoria
        brl_categories = ['Fundos Imobiliários', 'Ações Brasileiras', 'Propriedades']
        brl_dividends = recent_dividends[recent_dividends['category'].isin(brl_categories)]
        usd_dividends = recent_dividends[~recent_dividends['category'].isin(brl_categories)]

        # Filtrando os campos necessários
        brl_dividends_filtered = brl_dividends[['asset_ticker', 'value_per_share_brl', 'record_date', 'pay_date']]
        usd_dividends_filtered = usd_dividends[['asset_ticker', 'value_per_share_usd', 'record_date', 'pay_date']]

        # Unindo o DataFrame histórico filtrado com o DataFrame filtrado de dividendos brasileiros
        brl_dividends_final = pd.concat([historical_dividends_filtered, brl_dividends_filtered], ignore_index=True)

        # Removendo a coluna 'record_date', renomeando colunas e adicionando a coluna 'broker_name'
        brl_dividends_final = brl_dividends_final.drop(columns=['record_date'])
        brl_dividends_final = brl_dividends_final.rename(columns={'value_per_share_brl': 'transaction_amount', 'pay_date': 'transaction_date'})
        brl_dividends_final['broker_name'] = 'Itaú'

        usd_dividends_filtered = usd_dividends_filtered.drop(columns=['record_date'])
        usd_dividends_filtered = usd_dividends_filtered.rename(columns={'value_per_share_usd': 'transaction_amount', 'pay_date': 'transaction_date'})
        usd_dividends_filtered['broker_name'] = 'Charles Schwab'

        # Adicionando um dia às datas das transações
        brl_dividends_final['transaction_date'] = pd.to_datetime(brl_dividends_final['transaction_date']) + timedelta(days=1)
        usd_dividends_filtered['transaction_date'] = pd.to_datetime(usd_dividends_filtered['transaction_date']) + timedelta(days=1)

        # Unindo os DataFrames BRL e USD
        dividend_receive_events = pd.concat([brl_dividends_final, usd_dividends_filtered], ignore_index=True)

        # Salvando o DataFrame combinado em um novo arquivo CSV
        dividend_receive_events_csv_filepath = f'{csv_directory}/dividend_receive_events.csv'
        dividend_receive_events.to_csv(dividend_receive_events_csv_filepath, index=False)

        # Imprimindo os DataFrames resultantes
        print("BRL Dividends Final (with Historical Data):")
        print(brl_dividends_final)
        print("\nUSD Dividends (Filtered, including ETFs):")
        print(usd_dividends_filtered)
        print("\nDividend Receive Events:")
        print(dividend_receive_events)
