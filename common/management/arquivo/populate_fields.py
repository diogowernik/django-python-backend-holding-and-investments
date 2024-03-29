from django.core.management.base import BaseCommand
from timewarp.models import AssetHistoricalPrice
from datetime import datetime

class Command(BaseCommand):
    
    def add_historical_data(self, asset_id, currency, data):
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

        self.stdout.write(self.style.SUCCESS(f'Dados históricos de preços para o ativo {asset_id} inseridos com sucesso.'))

    def handle(self, *args, **kwargs):

        asset_data = [
            # {
            #     "asset_id": 223,  # este é o id do ativo no app # AP 312 - Lago Norte
            #     "currency": "BRL",
            #     "data": [
            #         ('2006-01-01', 187.5),
            #         ('2007-01-01', 240.7),
            #         ('2008-01-01', 293.9),
            #         ('2009-01-01', 347.1),
            #         ('2010-01-01', 400.3),
            #         ('2011-01-01', 453.5),
            #         ('2012-01-01', 520.0),
            #         ('2013-01-01', 503.5),
            #         ('2014-01-01', 487.0),
            #         ('2015-01-01', 470.5),
            #         ('2016-01-01', 420.0),
            #         ('2017-01-01', 435.0),
            #         ('2018-01-01', 450.0),
            #         ('2019-01-01', 465.0),
            #         ('2020-01-01', 480.0),
            #         ('2021-01-01', 495.0),
            #     ],
            # },
            {
                "asset_id": 224,  # este é o id do ativo no app # Ap 233 - Lago Norte
                "currency": "BRL",
                "data": [
                    ('2009-01-01', 120.00),
                    ('2010-01-01', 137.84),  
                    ('2011-01-01', 156.52),  
                    ('2012-01-01', 198.13), 
                    ('2013-01-01', 202.21), 
                    ('2014-01-01', 186.57),  
                    ('2015-01-01', 161.18),  
                    ('2016-01-01', 153.76), 
                    ('2017-01-01', 178.65),  
                    ('2018-01-01', 203.71),  
                    ('2019-01-01', 208.94),  
                    ('2020-01-01', 214.36),  
                    ('2021-01-01', 225.00),  
                ],
            },
            {
                "asset_id": 206,  # este é o id do ativo no app # Kit 320 D - Lago Norte
                "currency": "BRL",
                "data": [
                    ('2008-01-01', 77.7),
                    ('2009-01-01', 115),
                    ('2010-01-01', 155),
                    ('2011-01-01', 200),
                    ('2012-01-01', 230),
                    ('2013-01-01', 235),
                    ('2014-01-01', 220),
                    ('2015-01-01', 210),
                    ('2016-01-01', 200),
                    ('2017-01-01', 210),
                    ('2018-01-01', 220),
                    ('2019-01-01', 230),
                    ('2020-01-01', 232),
                    ('2021-01-01', 236),
                    ('2022-01-01', 238),
                    ('2023-01-01', 240),
                ],
            },
            {
                "asset_id": 20,  # este é o id do ativo no app # kit 204 B Aguas Claras
                "currency": "BRL",
                "data": [
                    ('2010-01-01', 56.763),
                    ('2011-01-01', 60.30713),
                    ('2012-01-01', 68.36294),
                    ('2013-01-01', 75.01614),
                    ('2014-01-01', 82.35888),
                    ('2015-01-01', 90.49005),
                    ('2016-01-01', 99.51645),
                    ('2017-01-01', 109.55302),
                    ('2018-01-01', 120.72426),
                    ('2019-01-01', 133.16478),
                    ('2020-01-01', 147.01993),
                    ('2021-01-01', 162.44720),
                    ('2022-01-01', 179.61679),
                    ('2023-01-01', 198.713),
                ],
            },
            {
                "asset_id": 19,  # este é o id do ativo no app # kit 106 B Aguas Claras
                "currency": "BRL",
                "data": [
                    ('2009-01-01', 42.761),
                    ('2010-01-01', 58.1369),
                    ('2011-01-01', 66.3509),
                    ('2012-01-01', 73.2333),
                    ('2013-01-01', 80.8597),
                    ('2014-01-01', 89.3101),
                    ('2015-01-01', 98.6687),
                    ('2016-01-01', 109.0241),
                    ('2017-01-01', 120.4698),
                    ('2018-01-01', 133.1042),
                    ('2019-01-01', 147.0308),
                    ('2020-01-01', 162.3581),
                    ('2021-01-01', 179.2003),
                    ('2022-01-01', 187.6770),
                    ('2023-01-01', 207.9153),
                ],
            },
        ]

        for asset in asset_data:
            self.add_historical_data(asset["asset_id"], asset["currency"], asset["data"])

        
        

