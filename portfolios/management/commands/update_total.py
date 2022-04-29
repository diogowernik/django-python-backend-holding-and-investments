from unicodedata import name
import pandas as pd
from django.core.management.base import BaseCommand
import yfinance as yf
from sqlalchemy import create_engine
import datetime
from portfolios.models import PortfolioAsset
from django.db.models import Q


class Command(BaseCommand):

    def handle(self, *args, **options):
        # get portfolio assets from db that will be updated
        queryset = PortfolioAsset.objects.values_list(
            "id", "asset__ticker", "asset__price", "shares_amount", "total_today_brl")
        app_df = pd.DataFrame(list(queryset), columns=[
            "id", "ticker", "price", "shares_amount", "total_today_brl"])
        app_df['total_today_brl'] = app_df['shares_amount'] * app_df['price']
        # set index
        app_df = app_df.set_index('id')
        print(app_df)

        for index, row in app_df.iterrows():
            try:
                portfolio_asset = PortfolioAsset.objects.get(id=index)
                portfolio_asset.total_today_brl = row['total_today_brl']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e} - {index}')
                pass
