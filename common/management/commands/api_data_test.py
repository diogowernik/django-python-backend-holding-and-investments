# update trade price
from tokenize import group
import pandas as pd
from django.core.management.base import BaseCommand
import requests
from common.utils.get_prices_from_api import fetch_asset_price_from_api




class Command(BaseCommand):

    def handle(self, *args, **options):
        # Testando a função fetch_asset_price_from_api na moeda original

        price_hglg11 = fetch_asset_price_from_api('HGLG11', 'BRL', 'BRL', '2023-07-08')
        self.stdout.write(self.style.SUCCESS(f'Preço para HGLG11: {price_hglg11}'))

        price_btc = fetch_asset_price_from_api('BTC', 'USD', 'USD', '2023-07-08')
        self.stdout.write(self.style.SUCCESS(f'BTC price_usd: {price_btc}'))


        price_apple = fetch_asset_price_from_api('AAPL', 'USD', 'USD', '2023-07-08')
        self.stdout.write(self.style.SUCCESS(f'AAPL price_usd: {price_apple}'))

        # Testando a função fetch_asset_price_from_api em outra moeda
        price_hglg11 = fetch_asset_price_from_api('HGLG11', 'BRL', 'USD', '2023-07-08')
        self.stdout.write(self.style.SUCCESS(f'HGLG11 price_usd: {price_hglg11}'))

        price_apple = fetch_asset_price_from_api('AAPL','USD', 'BRL', '2023-07-08')
        self.stdout.write(self.style.SUCCESS(f'AAPL price_brl: {price_apple}'))
        