import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioDividend


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Portfolio Average Price USD")
        # get portfolio assets from db and update total today
        queryset = PortfolioDividend.objects.values_list(
            "id", "average_price_usd", "average_price_brl", "usd_on_pay_date")
        app_df = pd.DataFrame(list(queryset), columns=[
            "id", "average_price_usd", "average_price_brl", "usd_on_pay_date"])
        app_df['average_price_usd'] = app_df['average_price_brl'] / \
            app_df['usd_on_pay_date']
        # round
        app_df['average_price_usd'] = app_df['average_price_usd'].round(2)
        # set index
        app_df = app_df.set_index('id')
        print(app_df)

        for index, row in app_df.iterrows():
            try:
                portfolio_asset = PortfolioDividend.objects.get(id=index)
                portfolio_asset.average_price_usd = row['average_price_usd']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e} - {index}')
                pass
        print("Average Price USD updated")
