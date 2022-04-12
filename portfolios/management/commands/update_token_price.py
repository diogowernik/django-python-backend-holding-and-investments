import datetime
# import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import PortfolioToken, PortfolioAsset
# from sqlalchemy import create_engine
from django.db.models import Sum


class Command(BaseCommand):
    help = "A command to create Portfolio Token and Update total value"

    # def handle(self, *args, **options):
    #     portfolio_total = PortfolioAsset.objects.aggregate(Sum('total_today_brl')).values()
    #     portfolio_total = float([x for x in portfolio_total][0])
    #     PortfolioToken.objects.create(
    #         # transaction_id=self.id,
    #         portfolio_id = 1,
    #         date = datetime.date.today(),
    #         total_today_brl= portfolio_total,
    #         order_value=0
    #     )
        
    #     print()
    