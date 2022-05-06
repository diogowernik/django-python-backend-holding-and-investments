import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset, Currency


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Currency price from economia")
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

        # get Currency price from economia
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/{app_list}').T.reset_index()
        economia_df = economia_df[['code', 'bid']]
        economia_df.columns = ['ticker', 'price']

        # print(economia_df)

        # config app_df to merge and economia_df
        app_df['ticker'] = app_df['ticker'].map(lambda x: x.rstrip('-BRL'))
        app_df = app_df.set_index('ticker')
        # print(app_df)

        # Merge app_df and economia_df
        df = app_df.merge(economia_df, left_on="ticker",
                          right_on="ticker", how='inner')
        # print(df)

        # Update Currency price
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price = df.loc[index]['price']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Currency price updated")
