# update Stocks price
import pandas as pd
from django.core.management.base import BaseCommand
import yfinance as yf
from investments.models import Asset, Stocks


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Stocks price from yahoo finance")
        # get assets from db that will be updated
        queryset = Stocks.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_list = app_df["ticker"].astype(str).tolist()
        # print(app_list)
        # get price from yfinance (only from Stocks in db)
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
        # get usd-brl rate

        # update price from yahoo_df USD to BRL
        usd_price = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_price.bid = usd_price.bid.astype(float)
        usd_value = usd_price.bid[0]
        # print(usd_value)

        yahoo_df['price'] = yahoo_df['price'] * usd_value
        # print(yahoo_df)

        # config app_df to merge
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge app_df and yahoo_df
        df = app_df.merge(yahoo_df, left_on="ticker",
                          right_on="ticker", how='inner')
        # print(df)

        # Update Stocks price
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price = df.loc[index]['price']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Stocks price updated")
