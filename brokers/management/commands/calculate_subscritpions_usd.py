from django.core.management.base import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = 'Reads data from multiple CSV files, filters columns, calculates yearly out-of-pocket investment amounts with accumulated balance for USD events, and prints the results using Pandas'

    def handle(self, *args, **options):
        # Diretório onde os arquivos CSV estão armazenados
        csv_directory = 'brokers/management/'

        # Lendo os arquivos CSV relacionados aos Estados Unidos (USD)
        invest_usd_events = pd.read_csv(f'{csv_directory}/invest_usd_events.csv')
        divest_usd_events = pd.read_csv(f'{csv_directory}/divest_usd_events.csv')
        dividends_events = pd.read_csv(f'{csv_directory}/dividends_2019_2024.csv')

        # Filtrando as colunas necessárias
        invest_usd_filtered = invest_usd_events[['ticker', 'trade_date', 'price_usd', 'trade_amount']].copy()
        divest_usd_filtered = divest_usd_events[['ticker', 'trade_date', 'price_usd', 'trade_amount']].copy()
        dividends_filtered = dividends_events[['asset_ticker', 'pay_date', 'total_dividend_usd', 'category']].copy()

        # Filtrando os dividendos para remover ativos das categorias 'Fundos Imobiliários', 'Ações Brasileiras' e 'Propriedades'
        categories_to_exclude = ['Fundos Imobiliários', 'Ações Brasileiras', 'Propriedades']
        dividends_filtered = dividends_filtered[~dividends_filtered['category'].isin(categories_to_exclude)]

        # Manter apenas as colunas necessárias
        dividends_filtered = dividends_filtered[['asset_ticker', 'pay_date', 'total_dividend_usd']]

        # Convertendo as datas para datetime
        invest_usd_filtered.loc[:, 'trade_date'] = pd.to_datetime(invest_usd_filtered['trade_date'])
        divest_usd_filtered.loc[:, 'trade_date'] = pd.to_datetime(divest_usd_filtered['trade_date'])
        dividends_filtered.loc[:, 'pay_date'] = pd.to_datetime(dividends_filtered['pay_date'])

        # Adicionando colunas de ano
        invest_usd_filtered.loc[:, 'year'] = invest_usd_filtered['trade_date'].dt.year
        divest_usd_filtered.loc[:, 'year'] = divest_usd_filtered['trade_date'].dt.year
        dividends_filtered.loc[:, 'year'] = dividends_filtered['pay_date'].dt.year

        # Calculando o valor de aporte total dos investimentos
        invest_usd_filtered.loc[:, 'total_amount'] = invest_usd_filtered['price_usd'] * invest_usd_filtered['trade_amount']
        divest_usd_filtered.loc[:, 'total_received'] = divest_usd_filtered['price_usd'] * divest_usd_filtered['trade_amount']

        # Agrupando por ano e calculando o valor total por ano
        yearly_investments = invest_usd_filtered.groupby('year')['total_amount'].sum()
        yearly_divests = divest_usd_filtered.groupby('year')['total_received'].sum()
        yearly_dividends = dividends_filtered.groupby('year')['total_dividend_usd'].sum()

        # Inicializando variáveis para o cálculo do saldo acumulado
        years = range(min(yearly_investments.index.min(), yearly_divests.index.min(), yearly_dividends.index.min()), max(yearly_investments.index.max(), yearly_divests.index.max(), yearly_dividends.index.max()) + 1)
        
        # Calculando o valor que precisa ser tirado do bolso a cada ano
        yearly_out_of_pocket = pd.Series(0, index=years, dtype=float)
        accumulated_balance = pd.Series(0, index=years, dtype=float)

        for year in years:
            investments = yearly_investments.get(year, 0)
            divests = yearly_divests.get(year, 0)
            dividends = yearly_dividends.get(year, 0)

            previous_balance = accumulated_balance.get(year - 1, 0)
            out_of_pocket = investments - divests - dividends - previous_balance
            if out_of_pocket < 0:
                out_of_pocket = 0

            yearly_out_of_pocket[year] = out_of_pocket
            accumulated_balance[year] = previous_balance + divests + dividends - investments

        # Imprimindo os DataFrames relacionados aos Estados Unidos (USD)
        print("\nUSD Events:")
        print("\nInvest USD Events:")
        print(invest_usd_filtered.head())
        print("\nDivest USD Events:")
        print(divest_usd_filtered.head())
        print("\nDividend USD Events:")
        print(dividends_filtered.head())

        # Imprimindo os totais anuais de investimentos, desinvestimentos e dividendos
        print(f"\nTotal Investments by Year:")
        print(yearly_investments)
        print(f"\nTotal Divests by Year:")
        print(yearly_divests)
        print(f"\nTotal Dividends by Year:")
        print(yearly_dividends)

        # Imprimindo o valor que precisa ser tirado do bolso e o valor acumulado por ano
        print(f"\nYearly Out-of-Pocket Amounts:")
        print(yearly_out_of_pocket)
        print(f"\nAccumulated Balance by Year:")
        print(accumulated_balance)

