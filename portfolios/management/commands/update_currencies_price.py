import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset, Currency


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Currency price_brl from economia")
        # get assets from db that will be updated
        queryset = Currency.objects.values_list("id", "ticker")
        app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        app_df['ticker'] = app_df['ticker'].astype(str) + '-BRL'
        app_list = app_df["ticker"].astype(str).tolist()
        app_list.remove('BRL-BRL')

        app_list = ','.join(app_list)
        # print(app_list)

        # economia api url
        # http://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL

        # get Currency price_brl from economia
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/{app_list}').T.reset_index()
        economia_df = economia_df[['code', 'bid']]
        economia_df.columns = ['ticker', 'price_brl']
        economia_df['price_brl'] = economia_df['price_brl'].astype(
            float).round(2)
        # add line index = BRL and price_brl = 1.0
        economia_df = economia_df.append(
            {'ticker': 'BRL', 'price_brl': 1.0}, ignore_index=True)
        print('economia_df')
        print(economia_df)

        # config app_df to merge and economia_df
        queryset = Currency.objects.values_list("id", "ticker")
        currencies_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
        # add line index = BRL and price_brl = 1.0
        print('currencies_df')
        print(currencies_df)

        # Merge app_df and economia_df
        df = currencies_df.merge(economia_df, left_on="ticker",
                                 right_on="ticker", how='inner')
        # print(df)

        # get usd price today
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]

        # add new column price_usd = price_brl * usd_brl_price
        df['price_usd'] = df['price_brl'] / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        print('df')
        print(df)

        # Update Currency price_brl
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price_brl = df.loc[index]['price_brl']
                asset.price_usd = df.loc[index]['price_usd']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Currency price_brl updated")
