from unicodedata import name
# import pandas as pd
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
import datetime
# from portfolios.models import Transaction
# from investments.models import Asset, Crypto
# from django.db.models import Q
import sqlite3
import warnings
from datetime import datetime
from .updates_functions import *
import time

warnings.filterwarnings('ignore')

class Command(BaseCommand):

    def handle(self, *args, **options):
        def create_connection(db_file):
            conn = None
            try:
                conn = sqlite3.connect(db_file)
            except Exception as e:
                print(e)
            return conn
        # conn = create_engine('sqlite:///db.sqlite3')
        conn = create_connection('db.sqlite3')

        # while True:
            
        get_yahoo_price(conn, 'investments_fii')
            # get_yahoo_price(conn, 'br_stocks')
            # get_criptos_price(conn, 'criptos')

            # uf.get_derivatives_price(conn, 'calls')
            # uf.get_derivatives_price(conn, 'puts')
            
            # uf.update_total_today(conn, 'fiis', 'portfolio_fiis', 'fii_id')
            # uf.update_total_today(conn, 'br_stocks', 'portfolio_br_stocks', 'br_stock_id')
            # uf.update_total_today(conn, 'criptos', 'portfolio_criptos', 'cripto_id')

            # uf.update_fiis_table(conn, 'last_dividend')
            # uf.update_fiis_table(conn, 'last_yield')
            # uf.update_fiis_table(conn, 'six_m_yield')
            # uf.update_fiis_table(conn, 'twelve_m_yield')
            # uf.update_fiis_table(conn, 'p_vpa')

            # print("Ultima Atualização:")
            # print(datetime.now())
            # print('Próxima atualização em 15 minutos')
            # time.sleep(900)
