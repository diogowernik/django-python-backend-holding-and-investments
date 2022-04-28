from unicodedata import name
import pandas as pd
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
import datetime
from portfolios.models import Transaction
from investments.models import Asset, Crypto
from django.db.models import Q


class Command(BaseCommand):

    def handle(self, *args, **options):
        excel_file = "excel/mexc.xlsx"

        queryset = Crypto.objects.values_list('id', "ticker")
        df = pd.DataFrame(list(queryset), columns=['id', "ticker"])
        df = df.set_index('ticker')

        df_2 = pd.read_excel(excel_file)
        df_2 = df_2.dropna()
        df_2 = df_2[['Trading Pair', 'Side', 'Amount', 'Average filled price']]
        df_2.columns = ['ticker', 'order', 'shares_amount', 'share_cost_usd']
        df_2['ticker'] = df_2['ticker'].str.replace('/USDT', '')
        df_2['share_cost_usd'] = df_2['share_cost_usd'].str.replace('USDT', '')
        df_2['shares_amount'] = df_2['shares_amount'].str.replace(
            '[A-Z]', '', regex=True)
        df_2 = df_2.set_index('ticker')
        df_2 = df_2.merge(df, left_on="ticker", right_on="ticker",
                          how='inner').set_axis(df_2.index)
        try:
            print(df_2)
        except Exception as e:
            print(f' Key Exception - {e}')
            pass

        for index, row in df_2.iterrows():
            try:
                Transaction.objects.create(
                    date=datetime.date.today(),
                    order=df_2.loc[index]['order'],
                    portfolio_id=1,
                    asset_id=df_2.loc[index]['id'],
                    broker_id=5,
                    shares_amount=float(df_2.loc[index]['shares_amount']),
                    share_cost_brl=float(df_2.loc[index]['share_cost_usd']),
                )
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        # engine = create_engine('sqlite:///db.sqlite3')

        # df.to_sql(Broker._meta.db_table, if_exists='append', con=engine, index=False)
