import pandas as pd
from django.core.management.base import BaseCommand
from investments.models import Asset
from portfolios.models import PortfolioAsset


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating total today usd")
        # get assets from db that will be updated
        queryset = PortfolioAsset.objects.values_list("id", "id",
                                                      "total_today_usd", "total_today_brl",
                                                      "share_average_price_brl", "total_cost_brl",
                                                      "share_average_price_usd", "total_cost_usd"
                                                      )
        df = pd.DataFrame(list(queryset), columns=["id", "index_id",
                                                   "total_today_usd", "total_today_brl", "share_average_price_brl", "total_cost_brl", "share_average_price_usd", "total_cost_usd"
                                                   ])

        # print(df_2.head())

        # get usd price from economia api
        economia_df = pd.read_json(
            f'https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
        usd_brl_price = economia_df['bid'].astype(float)[0]
        # print(usd_brl_price)

        df['total_today_usd'] = df['total_today_brl'] / usd_brl_price
        df['total_today_usd'] = df['total_today_usd'].round(2)
        df['share_average_price_usd'] = df['share_average_price_brl'] / usd_brl_price
        df['share_average_price_usd'] = df['share_average_price_usd'].round(2)

        df = df.set_index("index_id")

        # print(df)

        for index, row in df.iterrows():
            try:
                portfolio_asset = PortfolioAsset.objects.get(
                    id=df.loc[index]['id'])
                portfolio_asset.total_today_usd = df.loc[index]['total_today_usd']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e}')
                pass
        print("Total today usd updated")

        # # for index, row in df.iterrows():
        # #     try:
        # #         portfolio_asset = PortfolioAsset.objects.get(
        # #             id=df.loc[index]['id'])
        # #         portfolio_asset.total_today_usd = df.loc[index]['total_today_usd']
        # #         portfolio_asset.save()
        # #     except Exception as e:
        # #         print(f' Key Exception - {e}')
        # #         pass
        # # print("total_today_usd updated")
