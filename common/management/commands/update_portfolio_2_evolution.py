from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment, PortfolioEvolution
from timewarp.models import CurrencyHistoricalPrice, AssetHistoricalPrice
from datetime import datetime, timedelta
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **options):
        portfolio_id = 4
        category_id = 1  # ID para Fundos Imobiliários
        start_year = 2022
        start_month = 2  # Fevereiro
        end_date = datetime.now().date()  # Data final (pode ser ajustada)

        start_date = datetime(start_year, start_month, 1).date()

        # Criar um DataFrame com os registros PortfolioEvolution existentes
        existing_records = pd.DataFrame(list(PortfolioEvolution.objects.filter(portfolio_id=portfolio_id).values()))
        if 'date' in existing_records.columns:
            # Converter 'date' para datetime.date em existing_records, se necessário
            existing_records['date'] = pd.to_datetime(existing_records['date']).dt.date
        else:
            print("Não há registros existentes.")

        print("Existing records:")
        print(existing_records)

        df_preview = pd.DataFrame()  # DataFrame para acumular os dados planejados

        while start_date <= end_date:
            total_value_brl, total_value_usd = self.calculate_portfolio_evolution(portfolio_id, category_id, start_date)
            # Acumulando os dados planejados usando pandas.concat
            new_row = pd.DataFrame([{
                'portfolio_id': portfolio_id,
                'date': start_date,
                'category_id': category_id,
                'category_total_brl': total_value_brl,
                'category_total_usd': total_value_usd
            }])
            df_preview = pd.concat([df_preview, new_row], ignore_index=True)
            start_date += timedelta(days=32)
            start_date = start_date.replace(day=1)

        print("Preview dos dados a serem salvos:")
        print(df_preview)

        # Filtrar os registros que já existem
        if 'date' in existing_records.columns:
            df_new_records = df_preview[~df_preview['date'].isin(existing_records['date'])]
        else:
            df_new_records = df_preview

        print("Registros que serão criados:")
        print(df_new_records)

#         # Criar novos registros usando get_or_create
        for _, row in df_new_records.iterrows():
            PortfolioEvolution.objects.get_or_create(
                portfolio_id=row['portfolio_id'],
                date=row['date'],
                category_id=row['category_id'],
                defaults={
                    'category_total_brl': row['category_total_brl'],
                    'category_total_usd': row['category_total_usd']
                }
            )

    def calculate_portfolio_evolution(self, portfolio_id, category_id, date):
        investments = PortfolioInvestment.objects.filter(
            portfolio_id=portfolio_id,
            asset__category_id=category_id
        )

        total_value_brl = 0
        total_value_usd = 0

        for investment in investments:
            historical_price = AssetHistoricalPrice.objects.filter(
                asset=investment.asset,
                date__lte=date
            ).order_by('-date').first()

            if historical_price:
                total_value_brl += historical_price.close * investment.shares_amount
                total_value_usd += self.convert_to_usd(historical_price.close, date) * investment.shares_amount

        return total_value_brl, total_value_usd

    def convert_to_usd(self, amount, date):
        currency_price = CurrencyHistoricalPrice.objects.filter(
            currency_pair='USDBRL', 
            date__lte=date
        ).order_by('-date').first()

        if currency_price:
            return amount / currency_price.close
        else:
            return 0

# # Para testar o comando, execute 'python manage.py <nome deste arquivo sem .py>'
