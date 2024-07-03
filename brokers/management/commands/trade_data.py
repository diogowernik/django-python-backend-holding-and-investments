from django.core.management.base import BaseCommand
import pandas as pd
from timewarp.models import CurrencyHistoricalPrice

def usd_price(date):
    try:
        currency_price = CurrencyHistoricalPrice.objects.filter(
            currency_pair="BRLUSD",
            date__lte=date
        ).latest('date')
        return currency_price.close
    except CurrencyHistoricalPrice.DoesNotExist:
        print(f"No currency price found for date {date}")
        return None

class Command(BaseCommand):
    help = 'Reads data from a CSV file, renames headers, processes data, categorizes tickers, separates it into specific events DataFrames, and prints them using Pandas'

    def handle(self, *args, **options):
        # Diretório onde o arquivo CSV está armazenado
        csv_directory = 'brokers/management/'
        csv_filename = 'trade_data.csv'  # Substitua pelo nome do seu arquivo CSV

        # Caminho completo do arquivo CSV
        csv_filepath = f'{csv_directory}/{csv_filename}'

        # Lendo o arquivo CSV usando Pandas
        data = pd.read_csv(csv_filepath)

        # Renomeando os cabeçalhos para os nomes usados no seu banco de dados
        data.rename(columns={
            'Ativo': 'ticker',
            'Data': 'trade_date',
            'Qtd': 'trade_amount',
            'Desp.': 'fees',
            'C/V': 'trade_type',
            'Saldo': 'balance'
        }, inplace=True)

        # Convertendo a data para o formato YYYY-MM-DD
        data['trade_date'] = pd.to_datetime(data['trade_date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

        # Removendo os prefixos do ticker
        data['ticker'] = data['ticker'].str.replace(r'^(B3:|NYSE:|NASDAQ:|CC:)', '', regex=True)

        # Listas de categorias e tickers correspondentes
        categories = {
            'Fundos Imobiliários': ['KNCA11', 'KDIF11', 'KNRI11', 'BRCO11', 'HGCR11', 'RVBI11', 'HGLG11', 'HGBS11', 'HGRE11', 'BTAL11', 'QAGR11', 'RZTR11', 'BTLG11', 'KISU11', 'BDIF11', 'OUFF11', 'VGIP11', 'HSAF11', 'BTRA11', 'OURE11', 'MORC11', 'GCRI11', 'CPTS11', 'VGHF11', 'RECR11', 'OULG11', 'HCTR11', 'DEVA11', 'TGAR11', 'BCRI11', 'BARI11', 'IRDM11', 'VRTA11', 'RBHY11', 'CVBI11', 'KNIP11', 'HCRI11', 'RRCI11', 'HGFF11', 'XPLG11', 'HLOG11', 'XPIN11', 'HGRU11', 'HFOF11', 'GGRC11', 'BCIA11', 'MGFF11', 'JSRE11', 'VVPR11', 'TRXF11', 'MXRF11', 'ALZR11', 'VISC11', 'RECT11', 'RBVA11', 'IBFF11', 'HSML11', 'MCCI11', 'XPML11', 'BCFF11', 'MALL11', 'RBED11', 'LVBI11', 'NSLU11', 'OUJP11', 'FOFT11', 'FIGS11', 'BRCR11', 'KNCR11'],
            'Ações Brasileiras': ['BBDC4', 'UNIP6', 'SHUL4', 'SANB11', 'PSSA3', 'VIVT3', 'CSAN3', 'AURE3', 'EGIE3', 'SLCE3', 'CXSE3', 'BBSE3', 'KLBN4', 'RANI3', 'ITSA4', 'WEGE3', 'AESB3', 'TAEE11', 'SAPR4', 'VBBR3', 'IRBR3', 'BBAS3', 'TRPL4', 'TIET4', 'ELET6', 'WIZS3', 'CSMG3', 'EQTL3', 'VIVT4', 'ITUB4', 'ODPV3', 'ABCB4', 'TRPL3', 'SAPR3', 'ALUP4', 'ITUB3', 'BBDC3', 'CMIG3', 'SANB4', 'NEOE3', 'ENBR3', 'CPLE3', 'CGAS3', 'B3SA3', 'VLID3', 'UCAS3', 'EZTC3', 'LEVE3', 'CGAS5', 'TIMP3', 'SULA4', 'CPLE6', 'SBSP3', 'ATOM3', 'YDUQ3', 'TUPY3', 'MGLU3', 'MDIA3', 'CMIG4', 'CIEL3', 'SEER3', 'ITSA3', 'BIDI4', 'ALUP3', 'TEND3', 'MRVE3', 'ABEV3', 'PTNT4', 'NTCO3', 'GRND3', 'HGTX3', 'SQIA3', 'FLRY3', 'COGN3', 'ALSC3', 'SMLS3', 'SAPR11'],
            'ETFs': ['DIVD11', 'NDIV11', 'URNM', 'EIS', 'BIBL', 'MDIV', 'PGX', 'PFF', 'EMLC', 'SPFF', 'DIV'],
            'US Equities': ['DPZ', 'MA', 'BTC', 'MSFT', 'BAC', 'MCD', 'V', 'AXP', 'IBM', 'C', 'KO', 'JNJ', 'O', 'AAPL', 'SCHW', 'T', 'PEP', 'ADC', 'STAG', 'AVB', 'LTC', 'ESS', 'PSA', 'COST', 'HD', 'MAA', 'PLD', 'NNN', 'JPM', 'ARR', 'GOOD', 'INTC', 'NLY', 'VFC', 'BEN', 'SLG', 'BRMK', 'SBRA', 'MMM', 'EPR', 'VZ', 'PK', 'PBCT']
        }

        # Função para atribuir categorias
        def assign_category(ticker):
            for category, tickers in categories.items():
                if ticker in tickers:
                    return category
            return 'Unknown'

        # Aplicando a função para criar a coluna category_name
        data['category_name'] = data['ticker'].apply(assign_category)

        # Adicionando a coluna broker_name
        data['broker_name'] = data['currency'].apply(lambda x: 'Charles Schwab' if x == 'usd' else 'Itaú')

        # Separando os dados em dois DataFrames: um para BRL e outro para USD
        brl_data = data[data['currency'] == 'brl'].copy()
        usd_data = data[data['currency'] == 'usd'].copy()

        # Renomeando a coluna PU adequadamente
        brl_data.rename(columns={'PU': 'price_brl'}, inplace=True)
        usd_data.rename(columns={'PU': 'price_usd'}, inplace=True)

        # Adicionando a coluna price_usd ao DataFrame brl_data
        brl_data['price_usd'] = brl_data.apply(lambda row: row['price_brl'] / usd_price(row['trade_date']), axis=1)
        brl_data['price_usd'] = brl_data['price_usd'].round(2)

        # Adicionando a coluna price_brl ao DataFrame usd_data
        usd_data['price_brl'] = usd_data.apply(lambda row: row['price_usd'] * usd_price(row['trade_date']), axis=1)
        usd_data['price_brl'] = usd_data['price_brl'].round(2)

        # Separando os DataFrames derivados
        invest_br_events = brl_data[brl_data['trade_type'] == 'C']
        divest_br_events = brl_data[brl_data['trade_type'] == 'V']
        invest_usd_events = usd_data[usd_data['trade_type'] == 'C']
        divest_usd_events = usd_data[usd_data['trade_type'] == 'V']

        # Salvando os DataFrames derivados em arquivos CSV separados
        invest_br_events.to_csv(f'{csv_directory}/invest_br_events.csv', index=False)
        divest_br_events.to_csv(f'{csv_directory}/divest_br_events.csv', index=False)
        invest_usd_events.to_csv(f'{csv_directory}/invest_usd_events.csv', index=False)
        divest_usd_events.to_csv(f'{csv_directory}/divest_usd_events.csv', index=False)

        # Imprimindo os DataFrames derivados
        print("Invest BR Events:")
        print(invest_br_events[['ticker', 'trade_date', 'price_brl', 'price_usd', 'trade_amount', 'category_name', 'broker_name']])

        print("\nDivest BR Events:")
        print(divest_br_events[['ticker', 'trade_date', 'price_brl', 'price_usd', 'trade_amount', 'category_name', 'broker_name']])

        print("\nInvest USD Events:")
        print(invest_usd_events[['ticker', 'trade_date', 'price_usd', 'price_brl', 'trade_amount', 'category_name', 'broker_name']])

        print("\nDivest USD Events:")
        print(divest_usd_events[['ticker', 'trade_date', 'price_usd', 'price_brl', 'trade_amount', 'category_name', 'broker_name']])
