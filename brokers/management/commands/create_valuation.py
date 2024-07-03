from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime, timedelta
import os

class Command(BaseCommand):
    help = 'Creates a CSV file containing the first day of each month starting from 2006-06-01 at 18:00:00'

    def handle(self, *args, **options):
        # Definir a data inicial
        start_date = datetime(2006, 6, 1, 18, 0, 0)

        # Lista para armazenar as datas
        dates = []

        # Gerar datas do primeiro dia de cada mês
        current_date = start_date
        while current_date <= datetime.now():
            dates.append(current_date)
            # Adicionar um mês à data atual
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        # Criar um DataFrame com as datas
        df = pd.DataFrame({'date': dates})

        # Caminho do arquivo CSV
        csv_directory = 'brokers/management'
        csv_filepath = os.path.join(csv_directory, 'create_valuation.csv')

        # Salvar o DataFrame em um arquivo CSV
        df.to_csv(csv_filepath, index=False)

        self.stdout.write(self.style.SUCCESS(f"Arquivo CSV criado com sucesso em {csv_filepath}"))
