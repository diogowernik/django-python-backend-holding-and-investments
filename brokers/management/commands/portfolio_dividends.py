from django.core.management.base import BaseCommand
import pandas as pd
from portfolios.models import PortfolioDividend, Portfolio

class Command(BaseCommand):
    help = 'List all PortfolioDividend for portfolio ID 2 and create a pandas DataFrame'

    def handle(self, *args, **options):
        # Setup common attributes
        portfolio = Portfolio.objects.get(id=2)
        
        # Fetch all PortfolioDividend objects for the specified portfolio
        dividends = PortfolioDividend.objects.filter(portfolio=portfolio)

        # Create a list of dictionaries with the specified fields from PortfolioDividend
        dividend_data = []
        for dividend in dividends:
            dividend_data.append({
                'ticker': dividend.ticker,
                'category': dividend.category,
                'record_date': dividend.record_date,
                'pay_date': dividend.pay_date,
                'shares_amount': dividend.shares_amount,
                'value_per_share_brl': dividend.value_per_share_brl,
                'total_dividend_brl': dividend.total_dividend_brl,
                'average_price_brl': dividend.average_price_brl,
                'usd_on_pay_date': dividend.usd_on_pay_date,
                'value_per_share_usd': dividend.value_per_share_usd,
                'total_dividend_usd': dividend.total_dividend_usd,
                'average_price_usd': dividend.average_price_usd
            })

        # Create a DataFrame
        df = pd.DataFrame(dividend_data)

        # Save DataFrame to a CSV file
        file_path = 'brokers/management/dividends_2019_2024.csv'
        df.to_csv(file_path, index=False)
        print(f'Successfully created CSV at {file_path}')
