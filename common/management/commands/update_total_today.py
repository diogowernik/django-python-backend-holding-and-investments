import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Portfolio total")
        # get portfolio assets from db and update total today
        queryset = PortfolioInvestment.objects.values_list(
            "id", "asset__ticker", "asset__price_brl", "asset__price_usd", "shares_amount", 
            "total_today_brl", "total_today_usd", "total_cost_brl", "total_cost_usd")
        app_df = pd.DataFrame(list(queryset), columns=[
            "id", "ticker", "price_brl", "price_usd", "shares_amount", "total_today_br", "total_today_usd", "total_cost_brl", "total_cost_usd"])
        app_df['total_today_brl'] = app_df['shares_amount'] * \
            app_df['price_brl']
        app_df['total_today_usd'] = app_df['shares_amount'] * \
            app_df['price_usd']
        app_df['total_cost_brl'] = app_df['shares_amount'] * \
            app_df['price_brl']
        app_df['total_cost_usd'] = app_df['shares_amount'] * \
            app_df['price_usd']
        # set index
        app_df = app_df.set_index('id')
        # print(app_df)

        for index, row in app_df.iterrows():
            try:
                portfolio_asset = PortfolioInvestment.objects.get(id=index)
                portfolio_asset.total_today_brl = row['total_today_brl']
                portfolio_asset.total_today_usd = row['total_today_usd']
                portfolio_asset.total_cost_brl = row['total_cost_brl']
                portfolio_asset.total_cost_usd = row['total_cost_usd']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e} - {index}')
                pass
        print("Portfolio total updated")
