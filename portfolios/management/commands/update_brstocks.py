from django.core.management.base import BaseCommand
from investments.models import BrStocks
from investments.utils.common import fetch_data, rename_set_index, merge_dataframes, get_app_df, update_investment, update_ranking, preprocess_dataframe, update_prices_from_yahoo


class Command(BaseCommand):

    def handle(self, *args, **options):
        newline = "\n"
        bold_start = "\033[1m"
        bold_end = "\033[0m"

        print(f"{bold_start}Atualizando Ações Brasileiras...{bold_end}{newline}")

        # Fetching app data
        app_df = get_app_df(BrStocks)

        # Google fields from google sheets
        print(f"{newline}{bold_start}Atualizando preço em reais, topo e fundo 52 semanas, pela planilha do google...{bold_end}{newline}")

        google_brstocks_df = fetch_data('https://docs.google.com/spreadsheets/d/1-RnGncfUTlyYMSZZ6CHbLZtPLLhdKG8sGPNFeopbeHs/edit?usp=sharing')
        column_map_google = {'A': 'ticker', 'C': 'price_brl', 'D': 'top_52w', 'E': 'bottom_52w'}
        google_brstocks_df = rename_set_index(google_brstocks_df, column_map_google, 'ticker')
        merged_google_brstocks_df = merge_dataframes(app_df, google_brstocks_df, "ticker")
        print(merged_google_brstocks_df)
        update_investment(BrStocks, merged_google_brstocks_df, ['price_brl', 'top_52w', 'bottom_52w'])

        print(f"{newline}{bold_start}Feito.{bold_end}")

        # Fundamentus fileds from fundamentus.com.br
        print(f"{newline}{bold_start}Atualizando campos do fundamentus.com.br...{bold_end}{newline}")

        fundamentus_brstocks_df = fetch_data('https://www.fundamentus.com.br/resultado.php')
        column_map_fundamentus = {'Papel': 'ticker', 'P/L': 'pl', 'P/VP': 'p_vpa', 'PSR': 'psr',
                        'Div.Yield': 'twelve_m_yield', 'P/Ativo': 'p_ativo', 'P/Cap.Giro': 'p_cap_giro',
                        'P/EBIT': 'p_ebit', 'P/Ativ Circ.Liq': 'p_ativ_circ_liq', 'EV/EBIT': 'ev_ebit',
                        'EV/EBITDA': 'ev_ebitda', 'Mrg Ebit': 'mrg_ebit', 'Mrg. Líq.': 'mrg_liq',
                        'Liq. Corr.': 'liq_corr', 'ROIC': 'roic', 'ROE': 'roe', 'Liq.2meses': 'liq_2meses',
                        'Patrim. Líq': 'patrim_liq', 'Dív.Brut/ Patrim.': 'div_brut_patrim', 'Cresc. Rec.5a': 'cresc_rec_5a'}
    
        fundamentus_brstocks_df = rename_set_index(fundamentus_brstocks_df, column_map_fundamentus, 'ticker')
        transformations_for_fundamentus = {
            'twelve_m_yield': 'remove_percent',
            'roe': 'remove_percent',
            'roic': 'remove_percent',
            'p_vpa': 'divide_by_100',
            'pl': 'divide_by_100'
        }
        merged_fundamentus_brstocks_df = merge_dataframes(app_df, fundamentus_brstocks_df, "ticker")
        merged_fundamentus_brstocks_df = preprocess_dataframe(merged_fundamentus_brstocks_df, transformations_for_fundamentus)
        update_investment(BrStocks, merged_fundamentus_brstocks_df, ['twelve_m_yield', 'p_vpa', 'roe', 'roic', 'pl'])
        # print(merged_fundamentus_brstocks_df)
        update_ranking(BrStocks, "roe", "pl") # custom magic formula

        print(f"{newline}{bold_start}Feito.{bold_end}{newline}")

