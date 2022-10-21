import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioInvestment, PortfolioDividend


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Updating Total Dividends")
        queryset = PortfolioDividend.objects.values_list(
            "ticker", "total_dividend_brl",
            "total_dividend_usd"
        )
        df = pd.DataFrame(queryset, columns=[
                          "ticker", "total_dividend_brl",
                          "total_dividend_usd"
                          ])
        df = df.groupby("ticker").sum()
        df = df.reset_index()
        print(df)

        queryset = PortfolioInvestment.objects.values_list(
            "id", "asset__ticker", "dividends_profit_brl", "dividends_profit_usd")
        app_df = pd.DataFrame(list(queryset), columns=[
            "id", "ticker", "dividends_profit_brl", "dividends_profit_usd"])
        app_df = app_df.set_index('ticker')
        print(app_df)

        df = df.merge(app_df, on="ticker", how="left")
        df = df.dropna()
        df = df.set_index('id')
        print(df)

        for index, row in df.iterrows():
            try:
                portfolio_asset = PortfolioInvestment.objects.get(id=index)
                portfolio_asset.dividends_profit_brl = row['total_dividend_brl']
                portfolio_asset.dividends_profit_usd = row['total_dividend_usd']
                portfolio_asset.save()
            except Exception as e:
                print(f' Key Exception - {e} - {index}')
                pass
        print("Done")
