# update fiis price
from unicodedata import name
import pandas as pd
from django.core.management.base import BaseCommand
import yfinance as yf
from sqlalchemy import create_engine
import datetime
from portfolios.models import Transaction
from investments.models import Asset, Fii
from django.db.models import Q


class Command(BaseCommand):

    def handle(self, *args, **options):
        # get assets from db that will be updated
        queryset = Fii.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_list = app_df
        app_list['ticker'] = app_list['ticker'].astype(str) + '.SA'
        app_list = app_list["ticker"].astype(str).tolist()
        print(app_list)
        # get price from yfinance (only from fiis in db)
        yahoo_df = yf.download(app_list, period="1min")["Adj Close"]
        yahoo_df = yahoo_df.T.reset_index()
        # try in case of error
        try:
            yahoo_df.columns = ["ticker",  "price"]
            yahoo_df["price"] = yahoo_df["price"].round(2)
            yahoo_df['ticker'] = yahoo_df['ticker'].map(
                lambda x: x.rstrip('.SA'))
            yahoo_df = yahoo_df.set_index('ticker')
        except Exception as e:
            print(f' Key Exception - {e}')
            pass
        print(yahoo_df)

        # config app_df to merge
        app_df['ticker'] = app_df['ticker'].map(lambda x: x.rstrip('.SA'))
        app_df = app_df.set_index('ticker')
        print(app_df)

        # Merge app_df and yahoo_df
        df = app_df.merge(yahoo_df, left_on="ticker",
                          right_on="ticker", how='inner')
        print(df)

        # Update Fii price
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price = df.loc[index]['price']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
