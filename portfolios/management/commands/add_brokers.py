import pandas as pd
from django.core.management.base import BaseCommand
from portfolios.models import Broker
from sqlalchemy import create_engine

class Command(BaseCommand):
    help = "A command to add data from an Excel file to the database"

    def handle(self, *args, **options):
        
        engine = create_engine('sqlite:///db.sqlite3')
        # query = str(Broker.objects.all().query)
        # df = pd.read_sql_query(query, engine)

        df = pd.read_sql_query(f"SELECT investments_asset.ticker, investments_asset.price FROM investments_asset INNER JOIN investments_fii ON investments_asset.id=investments_fii.asset_ptr_id;", engine , index_col="ticker")
        
        print(df)


        # excel_file = "brokers.xlsx"
        # df = pd.read_excel(excel_file)

        # print(df)

        # engine = create_engine('sqlite:///db.sqlite3')

        # df.to_sql(Broker._meta.db_table, if_exists='append', con=engine, index=False)