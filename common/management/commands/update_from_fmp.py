import requests
from django.core.management.base import BaseCommand
import pandas as pd
from common.utils.fuctions import get_app_df, merge_dataframes, get_usd_to_brl_today, update_investment, update_ranking, create_df_from_api
from common.utils.get_financial_data import get_financial_data
from investments.models import Stocks, Reit, Etf
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.

api_key = os.getenv('API_KEY_FMP')

class Command(BaseCommand):
    def handle(self, *args, **options):

        newline = "\n"
        bold_start = "\033[1m"
        bold_end = "\033[0m"


        # Update Stocks
        print(f"{newline}{bold_start}Atualizando campos com dados do financialmodelingprep.com para Stocks...{bold_end}{newline}")
        

        app_df = get_app_df(Stocks)
        app_df = app_df[app_df['is_radar'] == True]
        app_df = app_df.drop(columns=['is_radar'])
        stocks_list = app_df.index.tolist()
        print(stocks_list)

        # less tickers to develop
        # stocks_list = ['MSFT', 'V']

        # get financial data
        merged_stocks_df = get_financial_data(stocks_list, api_key, app_df)
        print(merged_stocks_df)
        # update the database
        update_investment(Stocks, merged_stocks_df, ['twelve_m_dividend', 'der', 'ffo', 'p_ffo', 'p_vpa', 'roic', 'earnings_yield', 'price_usd', 'price_brl', 'ffo_yield'])
        # update ranking
        update_ranking(Stocks, 'roic', 'der') # earning yield original.


        # Update Reits
        print(f"{newline}{bold_start}Atualizando com dados do financialmodelingprep.com para Reits...{bold_end}{newline}")
        app_df = get_app_df(Reit)
        app_df = app_df[app_df['is_radar'] == True]
        app_df = app_df.drop(columns=['is_radar'])
        reits_list = app_df.index.tolist()

        # less tickers to develop
        # reits_list = ['PLD', 'ARE']

        # get financial data
        merged_reits_df = get_financial_data(reits_list, api_key, app_df)
        print(merged_reits_df)

        # update the database
        update_investment(Reit, merged_reits_df, ['twelve_m_dividend', 'der', 'ffo', 'p_ffo', 'p_vpa', 'roic', 'earnings_yield', 'price_usd', 'price_brl', 'ffo_yield'])

        # update ranking
        update_ranking(Reit, 'ffo_yield', 'der')

        # # Update Etf
        # print(f"{newline}{bold_start}Atualizando com dados do financialmodelingprep.com para Etf...{bold_end}{newline}")
        # app_df = get_app_df(Etf)
        # app_df = app_df[app_df['is_radar'] == True]
        # app_df = app_df.drop(columns=['is_radar'])
        # etf_list = app_df.index.tolist()

        # # less tickers to develop
        # # etf_list = ['DIV', 'PFF']

        # # get financial data
        # merged_etf_df = get_financial_data(etf_list, api_key, app_df)
        # print(merged_etf_df)

        # # update the database
        # update_investment(Etf, merged_etf_df, ['twelve_m_dividend', 'der', 'ffo', 'p_ffo', 'p_vpa', 'roic', 'earnings_yield', 'price_usd', 'price_brl', 'ffo_yield'])

        # # update ranking
        # update_ranking(Etf, 'ffo_yield', 'der')

        # print(f"{newline}{bold_start}Atualizando com dados do financialmodelingprep.com para Commodities...{bold_end}{newline}")
        
        
