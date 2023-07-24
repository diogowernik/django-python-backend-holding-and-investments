from django.core.management.base import BaseCommand
from timewarp.models import AssetHistoricalPrice
from datetime import datetime

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        asset_id = 223  # este é o id do ativo no app
        currency = "BRL"

        # Estes são os dados dos anos 2006 a 2021
        data = [
            ('2006-01-01', 187.5),
            ('2007-01-01', 240.7),
            ('2008-01-01', 293.9),
            ('2009-01-01', 347.1),
            ('2010-01-01', 400.3),
            ('2011-01-01', 453.5),
            ('2012-01-01', 520.0),
            ('2013-01-01', 503.5),
            ('2014-01-01', 487.0),
            ('2015-01-01', 470.5),
            ('2016-01-01', 420.0),
            ('2017-01-01', 435.0),
            ('2018-01-01', 450.0),
            ('2019-01-01', 465.0),
            ('2020-01-01', 480.0),
            ('2021-01-01', 495.0),
        ]

        for date_str, price in data:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            AssetHistoricalPrice.objects.create(
                asset_id=asset_id,
                currency=currency,
                date=date,
                open=price,
                high=price,
                low=price,
                close=price,
            )

        self.stdout.write(self.style.SUCCESS('Dados históricos de preços inseridos com sucesso.'))




        
        

