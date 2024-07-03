from django.core.management.base import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = 'Reads data from CSV files, filters, merges, and saves them using Pandas'

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

        # Criando DataFrames separados com base na categoria
        brl_categories = ['Fundos Imobiliários', 'Ações Brasileiras', 'Propriedades']
        brl_dividends = recent_dividends[recent_dividends['category'].isin(brl_categories)]
        usd_dividends = recent_dividends[~recent_dividends['category'].isin(brl_categories)]

        # Filtrando os campos necessários
        brl_dividends_filtered = brl_dividends[['asset_ticker', 'value_per_share_brl', 'record_date', 'pay_date']]
        usd_dividends_filtered = usd_dividends[['asset_ticker', 'value_per_share_usd', 'record_date', 'pay_date']]

        # Unindo o DataFrame histórico com o DataFrame filtrado de dividendos brasileiros
        brl_dividends_final = pd.concat([historical_dividends, brl_dividends_filtered], ignore_index=True)

        # Salvando os DataFrames em arquivos CSV separados
        brl_csv_filepath = f'{csv_directory}/dividend_br_events.csv'
        usd_csv_filepath = f'{csv_directory}/dividend_usd_events.csv'
        brl_dividends_final.to_csv(brl_csv_filepath, index=False)
        usd_dividends_filtered.to_csv(usd_csv_filepath, index=False)

        # Imprimindo os DataFrames
        print("BRL Dividends Final (with Historical Data):")
        print(brl_dividends_final)
        print("\nUSD Dividends (Filtered, including ETFs):")
        print(usd_dividends_filtered)
