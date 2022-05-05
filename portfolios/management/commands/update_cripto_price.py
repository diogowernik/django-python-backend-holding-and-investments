import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset, Crypto


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Cripto price from Coingecko")
        # get assets from db that will be updated
        queryset = Crypto.objects.values_list("id", "slug")
        app_df = pd.DataFrame(list(queryset), columns=["id", "slug"])
        app_list = app_df["slug"].astype(str).tolist()
        app_list = ','.join(app_list)
        # print(app_list)

        # coingecko api url
        # https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1

        # get crypto price from coingecko
        coingecko_df = pd.read_json(
            f'https://api.coingecko.com/api/v3/simple/price?ids={app_list}&vs_currencies=brl').T.reset_index()
        coingecko_df.columns = ["slug", "price"]
        coingecko_df = coingecko_df.set_index('slug')
        # print(coingecko_df)

        # config app_df to merge and coingecko_df
        app_df = app_df.set_index('slug')
        # print(app_df)

        # Merge app_df and coingecko_df
        df = app_df.merge(coingecko_df, left_on="slug",
                          right_on="slug", how='inner')
        # print(df)

        # Update Crypto price
        for index, row in df.iterrows():
            try:
                asset = Asset.objects.get(id=df.loc[index]['id'])
                asset.price = df.loc[index]['price']
                asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Crypto price updated")
