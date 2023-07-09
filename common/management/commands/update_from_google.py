from django.core.management.base import BaseCommand
from investments.models import BrStocks, Fii, Stocks, Reit
from common.utils.fuctions import fetch_data, rename_set_index, merge_dataframes, get_app_df, update_investment

def update_data_from_google(AppModel, sheet_url):
    newline = "\n"
    bold_start = "\033[1m"
    bold_end = "\033[0m"

    print(f"{bold_start}Atualizando {AppModel.__name__}...{bold_end}")

    # Fetching app data
    app_df = get_app_df(AppModel)

    # Google fields from google sheets
    print(f"{newline}{bold_start}Atualizando preço em reais, topo e fundo 52 semanas, pela planilha do google...{bold_end}{newline}")

    google_df = fetch_data(sheet_url)
    column_map_google = {'A': 'ticker', 'C': 'price_brl', 'D': 'top_52w', 'E': 'bottom_52w', 'F': 'price_usd'}
    google_df = rename_set_index(google_df, column_map_google, 'ticker')
    merged_google_df = merge_dataframes(app_df, google_df, "ticker")
    print(merged_google_df)
    update_investment(AppModel, merged_google_df, ['price_brl', 'top_52w', 'bottom_52w', 'price_usd'])

    print(f"{bold_start}Feito.{bold_end}{newline}")


class Command(BaseCommand):
    def handle(self, *args, **options):
        errors = []
        for model, url in [(BrStocks, 'https://docs.google.com/spreadsheets/d/1-RnGncfUTlyYMSZZ6CHbLZtPLLhdKG8sGPNFeopbeHs/edit?usp=sharing'), 
                           (Fii, 'https://docs.google.com/spreadsheets/d/1aOn6Fw_7arz-XcNB8KPIooK1Xgkg3lanRPh90PkB3O8/edit?usp=sharing'), 
                           (Stocks, 'https://docs.google.com/spreadsheets/d/18rUBtnbn0x9VarS2XUL3Vxs7ZyHlHR2v_RNBNn3VssE/edit?usp=sharing'), 
                           (Reit, 'https://docs.google.com/spreadsheets/d/16zJuluKOqz2rEqrQ2O_ijapdPsEshbBhOa-hRFn2Dl8/edit?usp=sharing')]:
            try:
                update_data_from_google(model, url)
            except Exception as e:
                errors.append(f"Erro ao atualizar {model.__name__}: {str(e)}")

        if errors:
            print("\n\033[1m Erros encontrados: \033[0m")
            for error in errors:
                print(error)
                print("\n")
