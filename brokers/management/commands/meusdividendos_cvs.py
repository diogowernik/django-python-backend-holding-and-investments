# meusdividendos_cvs.py
# python manage.py meusdividendos_cvs

import pandas as pd
from django.core.management.base import BaseCommand
import re

class Command(BaseCommand):
    help = 'Lê os dados de um arquivo CSV, filtra linhas desnecessárias, trata os dados e salva em um novo arquivo CSV'

    def handle(self, *args, **options):
        # Defina o caminho do arquivo CSV
        csv_file_path = 'meusdividendos_data.csv'
        output_csv_file_path = 'meusdividendos_data_tratado.csv'

        try:
            # Ler o arquivo CSV em um DataFrame pandas
            df = pd.read_csv(csv_file_path, delimiter=',', quotechar='"', thousands='.', decimal=',', skip_blank_lines=True)
            
            # Filtrar linhas válidas: manter apenas linhas onde a coluna 'Data' parece uma data válida
            date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
            df = df[df['Data'].apply(lambda x: bool(date_pattern.match(x)))]
            
            self.stdout.write(self.style.SUCCESS(f'Dados carregados com sucesso de {csv_file_path}'))

            # Extrair a moeda e converter o valor total
            df['currency'] = df['Total'].str.extract(r'^(brl|usd)\n', expand=False)
            df['Total'] = df['Total'].str.replace(r'^(brl|usd)\n', '', regex=True).str.replace('.', '').str.replace(',', '.').astype(float)
            
            # Reordenar colunas
            df = df[['Data', 'Ativo', 'C/V', 'Qtd', 'Saldo', 'PU', 'PM', 'Desp.', 'Total', 'currency']]

            # Salvar o DataFrame tratado em um novo arquivo CSV
            df.to_csv(output_csv_file_path, index=False)
            self.stdout.write(self.style.SUCCESS(f'Dados tratados e salvos em {output_csv_file_path}'))
            
            # Exibir as primeiras linhas do DataFrame tratado
            print(df.head())

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {csv_file_path}'))
        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR(f'O arquivo {csv_file_path} está vazio'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro ao ler o arquivo {csv_file_path}: {e}'))
