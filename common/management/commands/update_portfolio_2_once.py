from django.core.management.base import BaseCommand
from portfolios.models import PortfolioEvolution
from timewarp.models import CurrencyHistoricalPrice
from datetime import datetime, timedelta
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **options):
        portfolio_id = 4  # ID do seu portfólio
        renda_fixa_id = 7  # ID para Renda Fixa
        caixa_id = 4  # ID para Caixa

        start_date = datetime(2022, 2, 1)
        end_date = datetime.now()

        valor_caixa = 10  # Valor inicial para Caixa
        valor_renda_fixa = 50  # Valor inicial para Renda Fixa

        df_preview = pd.DataFrame()  # DataFrame para acumular os dados

        while start_date <= end_date:
            # Converter valores para USD
            valor_caixa_usd = self.convert_to_usd(valor_caixa, start_date)
            valor_renda_fixa_usd = self.convert_to_usd(valor_renda_fixa, start_date)

            # Acumulando os dados para pré-visualização
            df_preview = pd.concat([df_preview, pd.DataFrame([{
                'portfolio_id': portfolio_id, 
                'date': start_date, 
                'category_id': renda_fixa_id, 
                'category_total_brl': valor_renda_fixa,
                'category_total_usd': valor_renda_fixa_usd
            },{
                'portfolio_id': portfolio_id, 
                'date': start_date, 
                'category_id': caixa_id, 
                'category_total_brl': valor_caixa,
                'category_total_usd': valor_caixa_usd
            }])], ignore_index=True)

            # Preparar para o próximo mês
            start_date += timedelta(days=32)
            start_date = start_date.replace(day=1)
            valor_caixa += 12
            valor_renda_fixa += 160

        print("Preview dos dados a serem salvos:")
        print(df_preview)

        # Salvar os dados no banco de dados
        for _, row in df_preview.iterrows():
            PortfolioEvolution.objects.update_or_create(
                portfolio_id=row['portfolio_id'],
                date=row['date'],
                category_id=row['category_id'],
                defaults={
                    'category_total_brl': row['category_total_brl'],
                    'category_total_usd': row['category_total_usd']
                }
            )

        print("Dados de evolução do portfólio salvos com sucesso.")

    def convert_to_usd(self, amount, date):
        currency_price = CurrencyHistoricalPrice.objects.filter(
            currency_pair='USDBRL', 
            date__lte=date
        ).order_by('-date').first()

        if currency_price:
            return amount / currency_price.close
        else:
            return 0  # Pode ajustar conforme necessário

# Para testar o comando, execute 'python manage.py <nome deste arquivo sem .py>'

