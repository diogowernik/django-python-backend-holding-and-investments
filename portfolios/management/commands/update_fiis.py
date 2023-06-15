from django.core.management.base import BaseCommand
from investments.models import Fii
from investments.utils.common import fetch_data, rename_set_index, merge_dataframes, get_app_df, update_investment, update_ranking, preprocess_dataframe, update_prices_from_yahoo


class Command(BaseCommand):

    def handle(self, *args, **options):
        newline = "\n"
        bold_start = "\033[1m"
        bold_end = "\033[0m"

        print(f"{bold_start}Atualizando Fundos Imobiliários...{bold_end}{newline}")

        # Fetching app data
        app_df = get_app_df(Fii)

        # Google fields from google sheets
        print(f"{bold_start}Atualizando preço em reais, topo e fundo 52 semanas, pela planilha do google... ...{bold_end}{newline}")

        google_fiis_df = fetch_data(
            'https://docs.google.com/spreadsheets/d/1aOn6Fw_7arz-XcNB8KPIooK1Xgkg3lanRPh90PkB3O8/edit?usp=sharing')
        column_map_google = {'A': 'ticker', 'C': 'price_brl',
                             'D': 'top_52w', 'E': 'bottom_52w'}
        google_fiis_df = rename_set_index(google_fiis_df, column_map_google, 'ticker')
        merged_google_fiis_df = merge_dataframes(app_df, google_fiis_df, "ticker")
        print(merged_google_fiis_df)
        update_investment(Fii, merged_google_fiis_df, ['price_brl', 'top_52w', 'bottom_52w'])

        print(f"{newline}{bold_start}Feito.{bold_end}")

        # Fundamentus fileds from fundamentus.com.br
        print(
            f"{newline}{bold_start}Atualizando campos do fundamentus.com.br...{bold_end}{newline}")

        fundamentus_fiis_df = fetch_data(
            'https://www.fundamentus.com.br/fii_resultado.php')
        column_map_fundamentus = {'Papel': 'ticker', 'Segmento': 'setor', 'FFO Yield': 'ffo_yield', 'Dividend Yield': 'twelve_m_yield',
                                  'P/VP': 'p_vpa', 'Valor de Mercado': 'market_cap', 'Liquidez': 'liqudity',
                                  'Qtd de imóveis': 'assets', 'Preço do m2': 'price_m2', 'Aluguel por m2': 'rent_m2',
                                  'Cap Rate': 'cap_rate', 'Vacância Média': 'vacancy'}
        fundamentus_fiis_df = rename_set_index(fundamentus_fiis_df, column_map_fundamentus, 'ticker')
        merged_google_fiis_df = merge_dataframes(app_df, google_fiis_df, "ticker")
        transformations_for_fundamentus = {
            'twelve_m_yield': 'remove_percent',
            'p_vpa': 'divide_by_100'
        }
        merged_fundamentus_fiis_df = merge_dataframes(app_df, fundamentus_fiis_df, "ticker")
        merged_fundamentus_fiis_df = preprocess_dataframe(merged_fundamentus_fiis_df, transformations_for_fundamentus)
        print(merged_fundamentus_fiis_df)
        update_investment(Fii, merged_fundamentus_fiis_df, ['twelve_m_yield', 'p_vpa', 'assets'])
        update_ranking(Fii, "twelve_m_yield", "p_vpa")

        print(f"{newline}{bold_start}Feito.{bold_end}")
