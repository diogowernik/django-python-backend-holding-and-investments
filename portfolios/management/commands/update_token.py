import datetime
# import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import Portfolio, PortfolioAsset, PortfolioToken
# from sqlalchemy import create_engine
from django.db.models import Sum


class Command(BaseCommand):
    help = "A command to create Portfolio Token and Update total value"

    def handle(self, *args, **options):

        portfolios = Portfolio.objects.all()

        for portfolio in portfolios:
            portfolio_assets = PortfolioAsset.objects.filter(
                portfolio=portfolio)
            portfolio_total = portfolio_assets.aggregate(
                Sum('total_today_brl'))
            portfolio_total = portfolio_total['total_today_brl__sum']
            if portfolio_total is None:
                # ignore portfolio with no assets
                continue
            # float 2 decimal places
            portfolio_total = round(portfolio_total, 2)
            PortfolioToken.objects.create(
                portfolio=portfolio,
                date=datetime.date.today(),
                total_today_brl=portfolio_total,
                order_value=0
            )
            print(portfolio.name, portfolio_total)
        print('Updated PortfolioTokens')
