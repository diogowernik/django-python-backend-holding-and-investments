from django.core.management.base import BaseCommand
from investments.models import BrStocks, Fii, Stocks, Reit, Etf
from common.utils.fuctions import fetch_data, rename_set_index, merge_dataframes, get_app_df, update_investment, get_usd_to_brl_today
import pandas as pd

def update_data_from_google(AppModel, sheet_url):
    print(f"\033[1mAtualizando {AppModel.__name__}...\033[0m")

    # Pegamos o DataFrame do model (id, ticker, etc.)
    app_df = get_app_df(AppModel)

    # Lê a planilha do Google
    google_df = fetch_data(sheet_url)

    # Cotação atual do dólar
    usd_brl_price = get_usd_to_brl_today()
    print(f"Preço do dólar hoje: {usd_brl_price}")

    # Verifica se é ativo brasileiro ou americano
    if AppModel in [BrStocks, Fii]:
        # ------------------------------------------------
        # BRStocks e FII (campos em reais)
        # ------------------------------------------------
        column_map_google = {
            'A': 'ticker',
            'C': 'price_brl',
            'D': 'top_52w',
            'E': 'bottom_52w'
            # price_usd não existe mais aqui
        }
        google_df = rename_set_index(google_df, column_map_google, 'ticker')

        # Converte para float (caso venha com vírgula, etc.)
        google_df[['price_brl', 'top_52w', 'bottom_52w']] = google_df[[
            'price_brl', 'top_52w', 'bottom_52w'
        ]].apply(lambda col: col.astype(str).str.replace(',', '.').astype(float))

        # Calcula price_usd
        google_df['price_usd'] = (google_df['price_brl'] / usd_brl_price).round(2)

        # Faz merge no DF do App
        merged_google_df = merge_dataframes(app_df, google_df, "ticker")

        # Exibindo no console (pode usar to_string(), to_markdown(), etc.)
        print("\n\033[1mExibindo DataFrame (BR)\033[0m:")
        print(merged_google_df.to_string())  # ou .to_markdown(), .head(), etc.

        # Atualiza no banco
        update_investment(AppModel, merged_google_df,
                          ['price_brl', 'top_52w', 'bottom_52w', 'price_usd'])

    else:
        # ------------------------------------------------
        # Stocks, Reit, Etf (campos em dólares)
        # ------------------------------------------------
        column_map_google = {
            'A': 'ticker',
            'F': 'price_usd',
            'D': 'top_52w',
            'E': 'bottom_52w'
            # price_brl foi desativado na planilha
        }
        google_df = rename_set_index(google_df, column_map_google, 'ticker')

        # Converte para float
        google_df[['price_usd', 'top_52w', 'bottom_52w']] = google_df[[
            'price_usd', 'top_52w', 'bottom_52w'
        ]].apply(lambda col: col.astype(str).str.replace(',', '.').astype(float))

        # (Opcional) Se quiser calcular price_brl para guardar:
        google_df['price_brl'] = (google_df['price_usd'] * usd_brl_price).round(2)

        # Faz merge no DF do App
        merged_google_df = merge_dataframes(app_df, google_df, "ticker")

        print("\n\033[1mExibindo DataFrame (US)\033[0m:")
        print(merged_google_df.to_string())  # ou .to_markdown(), etc.

        # Atualiza no banco (aqui mantemos ambos, se seu model ainda tem price_brl)
        update_investment(AppModel, merged_google_df,
                          ['price_usd', 'price_brl', 'top_52w', 'bottom_52w'])

    print(f"\033[1mFeito {AppModel.__name__}.\033[0m\n")

class Command(BaseCommand):
    def handle(self, *args, **options):
        errors = []
        for model, url in [(BrStocks, 'https://docs.google.com/spreadsheets/d/1-RnGncfUTlyYMSZZ6CHbLZtPLLhdKG8sGPNFeopbeHs/edit?usp=sharing'), 
                           (Fii, 'https://docs.google.com/spreadsheets/d/1aOn6Fw_7arz-XcNB8KPIooK1Xgkg3lanRPh90PkB3O8/edit?usp=sharing'), 
                           (Stocks, 'https://docs.google.com/spreadsheets/d/18rUBtnbn0x9VarS2XUL3Vxs7ZyHlHR2v_RNBNn3VssE/edit?usp=sharing'), 
                           (Reit, 'https://docs.google.com/spreadsheets/d/16zJuluKOqz2rEqrQ2O_ijapdPsEshbBhOa-hRFn2Dl8/edit?usp=sharing'),
                           (Etf, 'https://docs.google.com/spreadsheets/d/1FZst_R7U8OhTMPb-Bu97dGOicO9uCsU2mE-ZfkY6heM/edit?usp=sharing')]:
            try:
                update_data_from_google(model, url)
            except Exception as e:
                errors.append(f"Erro ao atualizar {model.__name__}: {str(e)}")

        if errors:
            print("\n\033[1m Erros encontrados: \033[0m")
            for error in errors:
                print(error)
                print("\n")
