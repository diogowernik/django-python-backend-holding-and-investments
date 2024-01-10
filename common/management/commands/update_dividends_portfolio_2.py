from django.core.management.base import BaseCommand
from investments.models import Asset
from timewarp.models import CurrencyHistoricalPrice
from dividends.models import Dividend
from portfolios.models import PortfolioDividend, PortfolioInvestment
import requests
import pandas as pd
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        portfolio_id = 4

        # Obter PortfolioInvestments para o portfolio especificado
        portfolio_investments = PortfolioInvestment.objects.filter(portfolio_id=portfolio_id)

        # criar uma tabela do pandas com os dados de investimentos do portfólio com os campos: ticker, shares_amount, share_average_price_brl, share_average_price_usd, category
        df = pd.DataFrame(list(portfolio_investments.values('asset__ticker', 'shares_amount', 'share_average_price_brl', 'share_average_price_usd', 'asset__category__name')))
        # filter by category = 'Fundos Imobiliários'
        df = df[df['asset__category__name'] == 'Fundos Imobiliários']
        print(df)

        # criar pandas dataframe com os dados de dividendos filtrando por ticker
        dividends = Dividend.objects.filter(asset__ticker__in=df['asset__ticker'].tolist())
        df_dividends = pd.DataFrame(list(dividends.values('asset__ticker', 'record_date', 'pay_date', 'value_per_share_brl', 'value_per_share_usd')))
        print(df_dividends)

        # criar PortfolioDividends para cada Dividend

        for _, row in df_dividends.iterrows():
            # Pega o ticker e a data de pagamento do dividendo
            ticker = row['asset__ticker']
            pay_date = row['pay_date']

            # Filtra o DataFrame de investimentos para obter o número de ações e o preço médio
            filtered_investment = df[df['asset__ticker'] == ticker]

            if not filtered_investment.empty:
                shares_amount = filtered_investment.iloc[0]['shares_amount']
                average_price_brl = filtered_investment.iloc[0]['share_average_price_brl']
                average_price_usd = filtered_investment.iloc[0]['share_average_price_usd']

                # Calcular usd_on_pay_date
                if row['value_per_share_brl'] != 0:
                    usd_on_pay_date = row['value_per_share_usd'] / row['value_per_share_brl']
                else:
                    usd_on_pay_date = 0  # Caso value_per_share_brl seja zero

                # Calcular yield_on_cost
                if average_price_brl != 0:
                    yield_on_cost = (row['value_per_share_brl'] / average_price_brl) * 100
                else:
                    yield_on_cost = 0  # Caso average_price_brl seja zero

                # Dividend_tax será zero para FIIs
                dividend_tax = 0

                # Cria ou atualiza o PortfolioDividend
                PortfolioDividend.objects.update_or_create(
                    portfolio_id=portfolio_id,
                    ticker=ticker,
                    pay_date=pay_date,
                    defaults={
                        'record_date': row['record_date'],
                        'shares_amount': shares_amount,
                        'value_per_share_brl': row['value_per_share_brl'],
                        'total_dividend_brl': shares_amount * row['value_per_share_brl'],
                        'average_price_brl': average_price_brl,
                        'average_price_usd': average_price_usd,
                        'category': 'Fundos Imobiliários',
                        'subcategory': 'R',
                        'total_dividend_usd': shares_amount * row['value_per_share_usd'],
                        'usd_on_pay_date': usd_on_pay_date,
                        'dividend_tax': dividend_tax,
                        'yield_on_cost': yield_on_cost,
                        'value_per_share_usd': row['value_per_share_usd'],
                    }
                )

        print("Portfolio dividends updated.")



