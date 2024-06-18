import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioDividend
from datetime import datetime

class Command(BaseCommand):
    help = 'Update property rents for a given month and year'

    def add_arguments(self, parser):
        # Argumento opcional para o mês
        parser.add_argument('month', nargs='?', type=int, default=datetime.now().month)

        # Argumento opcional para o ano
        parser.add_argument('year', nargs='?', type=int, default=datetime.now().year)

    def handle(self, *args, **options):
        month = options['month']
        year = options['year']

        print(f"Updating Dividends for Properties for {month}/{year}...")

        # Define os ativos das propriedades com datas de pagamento variáveis e seus respectivos IDs de portfólio
        propriedades = [
            {'ticker': 'KIT 522', 'value_per_share': 1.20, 'average_price': 260.00, 'shares_amount': 1000.00, 'pay_date': 8, 'portfolio_id': 2},
            {'ticker': 'KIT 106 B', 'value_per_share': 0.93, 'average_price': 180.00, 'shares_amount': 1000.00, 'pay_date': 8, 'portfolio_id': 2},
            {'ticker': 'KIT 204 B', 'value_per_share': 0.85, 'average_price': 180.00, 'shares_amount': 1000.00, 'pay_date': 8, 'portfolio_id': 2},
            # A venda, sem dividendos
            # {'ticker': 'KIT 320 D', 'value_per_share': 0.90, 'average_price': 240.00, 'shares_amount': 334.00, 'pay_date': 8, 'portfolio_id': 2},
            {'ticker': 'CASA QL9', 'value_per_share': 0.80, 'average_price': 220.00, 'shares_amount': 3334.00, 'pay_date': 25, 'portfolio_id': 2},
            {'ticker': 'AP 315', 'value_per_share': 3.00, 'average_price': 900.00, 'shares_amount': 1000.00, 'pay_date': 8, 'portfolio_id': 7},
            {'ticker': 'Sala 906', 'value_per_share': 1.00, 'average_price': 180.00, 'shares_amount': 1000.00, 'pay_date': 8, 'portfolio_id': 7},
        ]

        # Obtenha o preço atual do USD
        economia_df = pd.read_json('https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        for prop in propriedades:
            try:
                total_dividend = round(prop['value_per_share'] * prop['shares_amount'], 2)

                # Verifica se já existe um registro, caso contrário, cria um novo
                obj, created = PortfolioDividend.objects.get_or_create(
                    portfolio_id=prop['portfolio_id'],
                    ticker=prop['ticker'],
                    record_date=datetime(year, month, 1),
                    defaults={ # Valores usados somente se um novo objeto for criado
                        'category': 'Propriedades',
                        'pay_date': datetime(year, month, prop['pay_date']),
                        'shares_amount': prop['shares_amount'],
                        'average_price_brl': prop['average_price'],
                        'average_price_usd': round(prop['average_price'] / usd_brl_price, 2),
                        'value_per_share_brl': prop['value_per_share'],
                        'total_dividend_brl': total_dividend,
                        'usd_on_pay_date': usd_brl_price,
                        'value_per_share_usd': round(prop['value_per_share'] / usd_brl_price, 2),
                        'total_dividend_usd': round(total_dividend / usd_brl_price, 2),
                    }
                )

                if not created:
                    print(f"Record already exists for {prop['ticker']} in {month}/{year}")

            except Exception as e:
                print(e)

        print("Property Dividends Updated!")

# Exemplo: python manage.py properties_rents 1 2021
# Caso não seja passado nenhum argumento, o mês e ano atual serão usados