import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment
from investments.utils.get_currency_price import get_exchange_rate


class Command(BaseCommand):

    def handle(self, *args, **options):
        exchange_rate = get_exchange_rate('USD', 'BRL', '2023-07-03')
        print(exchange_rate)
