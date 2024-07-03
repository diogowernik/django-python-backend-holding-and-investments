from django.core.management.base import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = 'Reads data from multiple CSV files, filters columns, calculates yearly out-of-pocket investment amounts with accumulated balance for BRL events, and prints the results using Pandas'

    def handle(self, *args, **options):
        # Diretório onde os arquivos CSV estão armazenados
        csv_directory = 'brokers/management/'

        # Lendo os arquivos CSV relacionados ao Brasil (BRL)
        invest_br_events = pd.read_csv(f'{csv_directory}/invest_br_events.csv')
        divest_br_events = pd.read_csv(f'{csv_directory}/divest_br_events.csv')
        dividends_events = pd.read_csv(f'{csv_directory}/dividends_2019_2024.csv')
        subscription_events = pd.read_csv(f'{csv_directory}/subscription_events.csv')
        property_invest_br_events = pd.read_csv(f'{csv_directory}/complete_property_invest_br_events.csv')
        property_divest_br_events = pd.read_csv(f'{csv_directory}/property_divest_br_events.csv')
        tax_pay_events = pd.read_csv(f'{csv_directory}/tax_pay_events.csv')
        properties_dividends = pd.read_csv(f'{csv_directory}/properties_dividends.csv')

        # Filtrando as colunas necessárias
        invest_br_filtered = invest_br_events[['ticker', 'trade_date', 'price_brl', 'trade_amount']].copy()
        divest_br_filtered = divest_br_events[['ticker', 'trade_date', 'price_brl', 'trade_amount']].copy()
        dividends_filtered = dividends_events[['asset_ticker', 'pay_date', 'total_dividend_brl', 'category']].copy()
        subscription_filtered = subscription_events[['transaction_date', 'transaction_amount']].copy()
        property_invest_filtered = property_invest_br_events[['asset_ticker', 'trade_amount', 'asset_price_brl', 'transaction_date']].copy()
        property_divest_filtered = property_divest_br_events[['asset_ticker', 'trade_amount', 'asset_price_brl', 'transaction_date']].copy()
        tax_pay_filtered = tax_pay_events[['transaction_date', 'transaction_amount']].copy()
        properties_dividends_filtered = properties_dividends[['asset_ticker', 'value_per_share_brl', 'pay_date']].copy()

        # Filtrando os dividendos para incluir apenas ativos das categorias 'Fundos Imobiliários', 'Ações Brasileiras' e 'Propriedades'
        categories_to_include = ['Fundos Imobiliários', 'Ações Brasileiras', 'Propriedades']
        dividends_filtered = dividends_filtered[dividends_filtered['category'].isin(categories_to_include)]

        # Manter apenas as colunas necessárias
        dividends_filtered = dividends_filtered[['asset_ticker', 'pay_date', 'total_dividend_brl']]

        # Convertendo as datas para datetime
        invest_br_filtered.loc[:, 'trade_date'] = pd.to_datetime(invest_br_filtered['trade_date'])
        divest_br_filtered.loc[:, 'trade_date'] = pd.to_datetime(divest_br_filtered['trade_date'])
        dividends_filtered.loc[:, 'pay_date'] = pd.to_datetime(dividends_filtered['pay_date'])
        subscription_filtered.loc[:, 'transaction_date'] = pd.to_datetime(subscription_filtered['transaction_date'])
        property_invest_filtered.loc[:, 'transaction_date'] = pd.to_datetime(property_invest_filtered['transaction_date'])
        property_divest_filtered.loc[:, 'transaction_date'] = pd.to_datetime(property_divest_filtered['transaction_date'])
        tax_pay_filtered.loc[:, 'transaction_date'] = pd.to_datetime(tax_pay_filtered['transaction_date'])
        properties_dividends_filtered.loc[:, 'pay_date'] = pd.to_datetime(properties_dividends_filtered['pay_date'])

        # Adicionando colunas de ano
        invest_br_filtered.loc[:, 'year'] = invest_br_filtered['trade_date'].dt.year
        divest_br_filtered.loc[:, 'year'] = divest_br_filtered['trade_date'].dt.year
        dividends_filtered.loc[:, 'year'] = dividends_filtered['pay_date'].dt.year
        subscription_filtered.loc[:, 'year'] = subscription_filtered['transaction_date'].dt.year
        property_invest_filtered.loc[:, 'year'] = property_invest_filtered['transaction_date'].dt.year
        property_divest_filtered.loc[:, 'year'] = property_divest_filtered['transaction_date'].dt.year
        tax_pay_filtered.loc[:, 'year'] = tax_pay_filtered['transaction_date'].dt.year
        properties_dividends_filtered.loc[:, 'year'] = properties_dividends_filtered['pay_date'].dt.year

        # Calculando o valor de aporte total dos investimentos
        invest_br_filtered.loc[:, 'total_amount'] = invest_br_filtered['price_brl'] * invest_br_filtered['trade_amount']
        divest_br_filtered.loc[:, 'total_received'] = divest_br_filtered['price_brl'] * divest_br_filtered['trade_amount']
        property_invest_filtered.loc[:, 'total_amount'] = property_invest_filtered['asset_price_brl'] * property_invest_filtered['trade_amount']
        property_divest_filtered.loc[:, 'total_received'] = property_divest_filtered['asset_price_brl'] * property_divest_filtered['trade_amount']

        # Calculando o valor total dos dividendos de propriedades
        properties_dividends_filtered.loc[:, 'total_dividend_brl'] = properties_dividends_filtered['value_per_share_brl'] * 1000

        # Agrupando por ano e calculando o valor total por ano
        yearly_investments = invest_br_filtered.groupby('year')['total_amount'].sum()
        yearly_divests = divest_br_filtered.groupby('year')['total_received'].sum()
        yearly_dividends = dividends_filtered.groupby('year')['total_dividend_brl'].sum()
        yearly_properties_dividends = properties_dividends_filtered.groupby('year')['total_dividend_brl'].sum()
        yearly_subscriptions = subscription_filtered.groupby('year')['transaction_amount'].sum()
        yearly_property_investments = property_invest_filtered.groupby('year')['total_amount'].sum()
        yearly_property_divests = property_divest_filtered.groupby('year')['total_received'].sum()
        yearly_tax_payments = tax_pay_filtered.groupby('year')['transaction_amount'].sum()

        # Inicializando variáveis para o cálculo do saldo acumulado
        years = range(min(yearly_investments.index.min(), yearly_divests.index.min(), yearly_dividends.index.min(), yearly_subscriptions.index.min(), yearly_property_investments.index.min(), yearly_property_divests.index.min(), yearly_tax_payments.index.min(), yearly_properties_dividends.index.min()), max(yearly_investments.index.max(), yearly_divests.index.max(), yearly_dividends.index.max(), yearly_subscriptions.index.max(), yearly_property_investments.index.max(), yearly_property_divests.index.max(), yearly_tax_payments.index.max(), yearly_properties_dividends.index.max()) + 1)
        
        # Calculando o valor que precisa ser tirado do bolso a cada ano
        yearly_out_of_pocket = pd.Series(0, index=years, dtype=float)
        accumulated_balance = pd.Series(0, index=years, dtype=float)

        for year in years:
            investments = yearly_investments.get(year, 0) + yearly_property_investments.get(year, 0) + yearly_tax_payments.get(year, 0)
            divests = yearly_divests.get(year, 0) + yearly_property_divests.get(year, 0)
            dividends = yearly_dividends.get(year, 0) + yearly_properties_dividends.get(year, 0)
            subscriptions = yearly_subscriptions.get(year, 0)

            previous_balance = accumulated_balance.get(year - 1, 0)
            out_of_pocket = investments - divests - dividends - subscriptions - previous_balance
            if out_of_pocket < 0:
                out_of_pocket = 0

            yearly_out_of_pocket[year] = out_of_pocket
            accumulated_balance[year] = previous_balance + divests + dividends + subscriptions - investments

        # Imprimindo os DataFrames relacionados ao Brasil (BRL)
        print("\nBRL Events:")
        print("\nInvest BR Events:")
        print(invest_br_filtered.head())
        print("\nDivest BR Events:")
        print(divest_br_filtered.head())
        print("\nDividend BR Events:")
        print(dividends_filtered.head())
        print("\nProperties Dividend Events:")
        print(properties_dividends_filtered.head())
        print("\nSubscription Events:")
        print(subscription_filtered.head())
        print("\nProperty Invest BR Events:")
        print(property_invest_filtered.head())
        print("\nProperty Divest BR Events:")
        print(property_divest_filtered.head())
        print("\nTax Pay Events:")
        print(tax_pay_filtered.head())

        # Imprimindo os totais anuais de investimentos, desinvestimentos e dividendos
        print(f"\nTotal Investments by Year:")
        print(yearly_investments)
        print(f"\nTotal Divests by Year:")
        print(yearly_divests)
        print(f"\nTotal Dividends by Year:")
        print(yearly_dividends)
        print(f"\nTotal Properties Dividends by Year:")
        print(yearly_properties_dividends)
        print(f"\nTotal Subscriptions by Year:")
        print(yearly_subscriptions)
        print(f"\nTotal Property Investments by Year:")
        print(yearly_property_investments)
        print(f"\nTotal Property Divests by Year:")
        print(yearly_property_divests)
        print(f"\nTotal Tax Payments by Year:")
        print(yearly_tax_payments)

        # Imprimindo o valor que precisa ser tirado do bolso e o valor acumulado por ano
        print(f"\nYearly Out-of-Pocket Amounts:")
        print(yearly_out_of_pocket)
        print(f"\nAccumulated Balance by Year:")
        print(accumulated_balance)

