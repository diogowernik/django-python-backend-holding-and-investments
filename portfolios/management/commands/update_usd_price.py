import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset
from portfolios.models import PortfolioAsset


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Currency price from economia")
        # get assets from db that will be updated
        queryset = Asset.objects.values_list(
            "id", "ticker", "price", "price_usd")
        df = pd.DataFrame(list(queryset), columns=[
            "id", "ticker", "price", "price_usd"])
        df = df.set_index("ticker")
        # print(df.head())

        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]
        # print(usd_brl_price)

        df['price_usd'] = df['price'] / usd_brl_price
        df['price_usd'] = df['price_usd'].round(2)
        # print(df.head())

        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price_usd = df.loc[index]['price_usd']
                asset.price_brl = df.loc[index]['price']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Currency price updated")

        # updated_df = Asset.objects.values_list(
        #     "id", "ticker", "price", "price_usd")
        # updated_df = pd.DataFrame(list(updated_df), columns=[
        #     "id", "ticker", "price", "price_usd"])
        # updated_df = updated_df.set_index("ticker")
        # print(updated_df.head())
