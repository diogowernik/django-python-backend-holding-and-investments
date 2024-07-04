from django.core.management.base import BaseCommand
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from financials.models import PortfolioDividend, AccumulatedDividends
import pandas as pd

class Command(BaseCommand):
    help = 'Aggregates monthly dividends for the last 20 years'

    def handle(self, *args, **options):
        start_date = datetime.now() - relativedelta(years=20)
        end_date = datetime.now()
        current_date = start_date

        results = []

        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            result = self.aggregate_dividends_for_month(year, month)
            results.append(result)
            current_date += relativedelta(months=1)

        # Opcional: Mostrar resultados com pandas antes de salvar no banco de dados
        df = pd.DataFrame(results)
        print(df)

        self.stdout.write(self.style.SUCCESS('Successfully aggregated dividends for the last 20 years'))

    def aggregate_dividends_for_month(self, year, month):
        dividends = PortfolioDividend.objects.filter(
            pay_date__year=year,
            pay_date__month=month
        ).values('portfolio_investment__portfolio').annotate(
            total_dividends_brl=Sum('value_per_share_brl'),
            total_dividends_usd=Sum('value_per_share_usd')
        )

        for dividend in dividends:
            portfolio_id = dividend['portfolio_investment__portfolio']
            total_brl = dividend['total_dividends_brl']
            total_usd = dividend['total_dividends_usd']

            # Criar ou atualizar o registro de dividendos acumulados
            accumulated_dividend, created = AccumulatedDividends.objects.update_or_create(
                portfolio_id=portfolio_id,
                year=year,
                month=month,
                defaults={
                    'accumulated_dividends_brl': total_brl,
                    'accumulated_dividends_usd': total_usd
                }
            )

            # Retornar dados para possível visualização com pandas
            return {
                'Year': year,
                'Month': month,
                'Portfolio': portfolio_id,
                'Dividends BRL': total_brl,
                'Dividends USD': total_usd
            }
