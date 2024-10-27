# update dividends from CSV
import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioDividend

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Dividends from CSV...")

        # Read the CSV file
        try:
            dividends = pd.read_csv('dividends_2024.csv')
            print("CSV file 'dividends_2024.csv' successfully loaded.")
        except FileNotFoundError:
            print("CSV file 'dividends_2024.csv' not found in the root directory.")
            return
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")
            return

        # Convert date columns to datetime
        dividends['record_date'] = pd.to_datetime(dividends['record_date'])
        dividends['pay_date'] = pd.to_datetime(dividends['pay_date'])

        # Convert numeric columns to appropriate data types
        numeric_columns = [
            'shares_amount', 'value_per_share_brl', 'total_dividend_brl',
            'average_price_brl', 'usd_on_pay_date', 'value_per_share_usd',
            'total_dividend_usd', 'average_price_usd'
        ]

        for column in numeric_columns:
            dividends[column] = pd.to_numeric(dividends[column], errors='coerce')

        # Drop rows with missing essential data
        dividends.dropna(subset=['asset_ticker', 'category', 'record_date', 'pay_date'], inplace=True)

        # Optionally process 'category' column if needed
        # For example, replace certain categories to standardize
        dividends['category'] = dividends['category'].str.replace('FII', 'Fundos Imobiliários')
        dividends['category'] = dividends['category'].str.replace('Ação', 'Ações Brasileiras')
        dividends['category'] = dividends['category'].str.replace('Stock', 'Stocks')
        dividends['category'] = dividends['category'].str.replace('REIT', 'REITs')

        # Loop through each dividend entry and create PortfolioDividend objects
        for index, row in dividends.iterrows():
            try:
                PortfolioDividend.objects.create(
                    portfolio_id=2,
                    ticker=row['asset_ticker'],
                    category=row['category'],
                    record_date=row['record_date'],
                    pay_date=row['pay_date'],
                    shares_amount=row['shares_amount'],
                    average_price_brl=row['average_price_brl'],
                    average_price_usd=row['average_price_usd'],
                    value_per_share_brl=row['value_per_share_brl'],
                    total_dividend_brl=row['total_dividend_brl'],
                    usd_on_pay_date=row['usd_on_pay_date'],
                    value_per_share_usd=row['value_per_share_usd'],
                    total_dividend_usd=row['total_dividend_usd'],
                )
                print(f"Dividend for {row['asset_ticker']} on {row['pay_date'].date()} added.")
            except Exception as e:
                print(f"Error adding dividend for {row['asset_ticker']}: {e}")
                continue

        print("Dividends Updated!")
