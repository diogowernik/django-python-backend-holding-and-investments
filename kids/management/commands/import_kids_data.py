import csv
from django.core.management.base import BaseCommand
from kids.models import KidsEarns, KidsExpenses, KidProfile
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Importa dados dos CSVs de KidsEarns e KidsExpenses para o banco de dados'

    def handle(self, *args, **kwargs):
        # Caminho para a pasta management
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório absoluto deste arquivo

        # Caminhos para os arquivos CSV (estão na pasta management)
        earns_csv = os.path.join(base_dir, 'kids_earns.csv')
        expenses_csv = os.path.join(base_dir, 'kids_expenses.csv')

        # Importação de KidsEarns
        self.import_kids_earns(earns_csv)
        
        # Importação de KidsExpenses
        self.import_kids_expenses(expenses_csv)

        self.stdout.write(self.style.SUCCESS('Dados importados com sucesso!'))

    def import_kids_earns(self, file_path):
        self.stdout.write(f"Importando KidsEarns do arquivo: {file_path}")
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Fixando o KidProfile para o id 4
                profile = KidProfile.objects.get(id=4)
                
                earn = KidsEarns(
                    belongs_to=profile,
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    description=row['description'],
                    amount=row['amount'],
                    category=row['category']
                )
                
                # Printando os dados para visualização
                print(f"Earn: {earn.date} - {earn.description} - {earn.amount} - {earn.category}")

                # Comentando a parte de salvar para revisão antes de inserir no banco
                earn.save()

    def import_kids_expenses(self, file_path):
        self.stdout.write(f"Importando KidsExpenses do arquivo: {file_path}")
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Fixando o KidProfile para o id 4
                profile = KidProfile.objects.get(id=4)
                
                expense = KidsExpenses(
                    belongs_to=profile,
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    description=row['description'],
                    amount=row['amount'],
                    category=row['category']
                )
                
                # Printando os dados para visualização
                print(f"Expense: {expense.date} - {expense.description} - {expense.amount} - {expense.category}")

                # Comentando a parte de salvar para revisão antes de inserir no banco
                expense.save()
