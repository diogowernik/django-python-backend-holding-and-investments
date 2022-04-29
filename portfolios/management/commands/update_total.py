import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioAsset


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Portfolio Asset total today brl")
        # get portfolio assets from db and update total today
        queryset = PortfolioAsset.objects.values_list(
            "id", "asset__ticker", "asset__price", "shares_amount", "total_today_brl")
        app_df = pd.DataFrame(list(queryset), columns=[
            "id", "ticker", "price", "shares_amount", "total_today_brl"])
        app_df['total_today_brl'] = app_df['shares_amount'] * app_df['price']
        # set index
        app_df = app_df.set_index('id')
        # print(app_df)

        for index, row in app_df.iterrows():
            try:
                portfolio_asset = PortfolioAsset.objects.get(id=index)
                portfolio_asset.total_today_brl = row['total_today_brl']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e} - {index}')
                pass
        print("Portfolio Asset total today brl updated")
