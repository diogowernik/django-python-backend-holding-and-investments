import pandas as pd
from django.core.management.base import BaseCommand
import yfinance as yf
from investments.models import Asset


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating BrStocks and Fiis price_brl and price_usd from yahoo finance")
        # get assets from db that will be updated
        queryset = Asset.objects.filter(category__in=['1', '9']).values_list(
            "id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=[
                              "id", "ticker"])
        app_df['ticker'] = app_df['ticker'].astype(str) + '.SA'
        app_list = app_df["ticker"].astype(str).tolist()

        # print(app_list)

        yahoo_df = yf.download(app_list, period="1min")["Adj Close"]
        yahoo_df = yahoo_df.T.reset_index()
        print("DataFrame após transposição e antes do processamento:")
        print(yahoo_df)
        if yahoo_df.shape[1] == 3:
            try:
                yahoo_df.columns = ["ticker",  "price_brl", "price_brl2"]
                yahoo_df["price_brl"] = yahoo_df["price_brl"].fillna(
                    yahoo_df["price_brl2"]).round(2)
                yahoo_df['ticker'] = yahoo_df['ticker'].map(
                    lambda x: x.rstrip('.SA'))
                yahoo_df = yahoo_df.set_index('ticker')
            except Exception as e:
                print(f' Key Exception 1 - {e}')
                # show ticker that has problem
                print(yahoo_df["ticker"])
                pass
        else:
            try:

                yahoo_df.columns = ["ticker",  "price_brl"]
                yahoo_df["price_brl"] = yahoo_df["price_brl"].round(2)
                yahoo_df['ticker'] = yahoo_df['ticker'].map(
                    lambda x: x.rstrip('.SA'))
                yahoo_df = yahoo_df.set_index('ticker')
            except Exception as e:
                print(f' Key Exception 2 - {e}')
                pass
        # print(yahoo_df)

        # config app_df to merge
        app_df['ticker'] = app_df['ticker'].map(lambda x: x.rstrip('.SA'))
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge app_df and yahoo_df
        df = app_df.merge(yahoo_df, left_on="ticker",
                          right_on="ticker", how='inner')
        print(df)

        # get usd price today
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl * usd_brl_price
        df['price_usd'] = df['price_brl'] / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        # print(df)

        # Update BrStock price_brl
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=row['id'])
                price_brl = row['price_brl']
                price_usd = row['price_usd']
                
                if price_brl is None or price_usd is None:
                    print(f"Missing price data for ticker {row['ticker']}: price_brl={price_brl}, price_usd={price_usd}")
                    continue

                asset.price_brl = price_brl
                asset.price_usd = price_usd
                asset.save()
            except Exception as e:
                ticker = df.loc[index, 'ticker'] if 'ticker' in df.columns else 'Unknown'
                print(f"Key Exception 3 - {e} for ticker: {ticker}")
                print("Asset ID:", row['id'])
                pass

        print("BrStocks and Fiis price_brl and price usd_update updated")


