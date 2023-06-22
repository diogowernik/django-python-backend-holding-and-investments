from django.core.management.base import BaseCommand
from investments.models import BrStocks, Fii
from investments.utils.common import fetch_data, rename_set_index, merge_dataframes, get_app_df, update_investment, update_ranking, preprocess_dataframe

def update_data_from_fundamentus(AppModel, fetch_url, column_map, transformations, update_fields, ranking1, ranking2):
    newline = "\n"
    bold_start = "\033[1m"
    bold_end = "\033[0m"

    print(f"{newline}{bold_start}Atualizando campos do fundamentus.com.br para {AppModel.__name__}...{bold_end}{newline}")

    # Fetching app data
    app_df = get_app_df(AppModel)

    fundamentus_df = fetch_data(fetch_url)
    fundamentus_df = rename_set_index(fundamentus_df, column_map, 'ticker')
    merged_fundamentus_df = merge_dataframes(app_df, fundamentus_df, "ticker")
    merged_fundamentus_df = preprocess_dataframe(merged_fundamentus_df, transformations)
    print(merged_fundamentus_df)
    update_investment(AppModel, merged_fundamentus_df, update_fields)
    update_ranking(AppModel, ranking1, ranking2)

    print(f"{newline}{bold_start}Feito.{bold_end}{newline}")

class Command(BaseCommand):
    def handle(self, *args, **options):
        errors = []

        try:
            update_data_from_fundamentus(
                Fii,
                'https://www.fundamentus.com.br/fii_resultado.php', 
                # Renomeia colunas
                {'Papel': 'ticker', 'Segmento': 'setor', 'FFO Yield': 'ffo_yield',
                'Dividend Yield': 'twelve_m_yield', 'P/VP': 'p_vpa',
                'Valor de Mercado': 'market_cap', 'Liquidez': 'liquidity',
                'Qtd de imóveis': 'assets', 'Preço do m2': 'price_m2',
                'Aluguel por m2': 'rent_m2', 'Cap Rate': 'cap_rate',
                'Vacância Média': 'vacancy'
                },
                # Transformações a serem aplicadas a certos campos
                {
                    'twelve_m_yield': 'remove_percent', 
                    'ffo_yield': 'remove_percent',
                    'cap_rate': 'remove_percent',
                    'vacancy': 'remove_percent',
                    'p_vpa': 'divide_by_100',
                    'price_m2': 'divide_by_100',
                    'rent_m2': 'divide_by_100',
                    'market_cap': 'remove_dot',
                    'liquidity': 'remove_dot',   
                 }, 
                 # Campos a serem atualizados
                ['twelve_m_yield', 'p_vpa', 'assets', 'price_m2', 'rent_m2', 'cap_rate', 'vacancy', 'ffo_yield', 'market_cap', 'liquidity'],
                # "magic formula" de ranking
                "ffo_yield", "p_vpa"
            )
        except Exception as e:
            errors.append(f"Erro ao atualizar Fii: {str(e)}")

        try:
            update_data_from_fundamentus(
                BrStocks,
                'https://www.fundamentus.com.br/resultado.php',
                # tabela renomeada para colunas iguais ao modelo do django
                {'Papel': 'ticker', 'P/L': 'pl', 'P/VP': 'p_vpa', 'PSR': 'psr',
                'Div.Yield': 'twelve_m_yield', 'P/Ativo': 'p_ativo',
                'P/Cap.Giro': 'p_cap_giro', 'P/EBIT': 'p_ebit',
                'P/Ativ Circ.Liq': 'p_ativ_circ_liq', 'EV/EBIT': 'ev_ebit',
                'EV/EBITDA': 'ev_ebitda', 'Mrg Ebit': 'mrg_ebit',
                'Mrg. Líq.': 'mrg_liq', 'Liq. Corr.': 'liq_corr',
                'ROIC': 'roic', 'ROE': 'roe', 'Liq.2meses': 'liq_2meses',
                'Patrim. Líq': 'patrim_liq', 'Dív.Brut/ Patrim.': 'div_brut_patrim',
                'Cresc. Rec.5a': 'cresc_rec_5a'
                },
                # Transformações a serem aplicadas a certos campos
                {
                'twelve_m_yield': 'remove_percent', 
                'roe': 'remove_percent',
                'roic': 'remove_percent', 
                'p_vpa': 'divide_by_100',
                'pl': 'divide_by_100'
                },
                # Atualiza no modelo
                ['twelve_m_yield', 'p_vpa', 'roe', 'roic', 'pl'],
                # "magic formula" de ranking
                "roe", "pl"
            )
        except Exception as e:
            errors.append(f"Erro ao atualizar BrStocks: {str(e)}")

        if errors:
            print("\nErros encontrados:")
            for error in errors:
                print(error)

