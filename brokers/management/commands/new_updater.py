# management/commands/portfolio_updater.py
from django.core.management.base import BaseCommand
from datetime import datetime
import pandas as pd

from .utils import (
    read_processed_batches,
    write_processed_batch,
    write_error_log_to_csv,
    split_events_by_date,
    convert_to_datetime,
    log_error,
    error_log
)

from .event_creators import (
    create_property_invest_br_event,
    create_property_divest_br_event,
    create_valuation_event,
    create_subscription_event,
    create_tax_pay_event,
    create_dividend_br_event,
    create_dividend_usd_event,
    create_transfer_event,
    create_or_update_asset_create_historical_price_create_invest_br_event,
    create_or_update_asset_create_historical_price_create_invest_us_event,
    create_divest_br_event,
    create_divest_us_event,
    send_money_event,
    create_dividend_distribution_event
)

class Command(BaseCommand):
    help = 'Creates all events from CSV files to populate the portfolio database'

    portfolio_id = 15

    def handle(self, *args, **options):
        # Diretório onde os arquivos CSV estão armazenados
        csv_directory = 'brokers/management/csv_files'

        # Carregando os arquivos CSV organizados
        subscription_events = pd.read_csv(f'{csv_directory}/subscription_events.csv')
        property_invest_br_events = pd.read_csv(f'{csv_directory}/property_invest_br_events.csv')
        property_divest_br_events = pd.read_csv(f'{csv_directory}/property_divest_br_events.csv')
        tax_pay_events = pd.read_csv(f'{csv_directory}/tax_pay_events.csv')
        invest_br_events = pd.read_csv(f'{csv_directory}/invest_br_events.csv')
        invest_usd_events = pd.read_csv(f'{csv_directory}/invest_usd_events.csv')
        divest_br_events = pd.read_csv(f'{csv_directory}/divest_br_events.csv')
        divest_usd_events = pd.read_csv(f'{csv_directory}/divest_usd_events.csv')
        dividend_br_events = pd.read_csv(f'{csv_directory}/dividend_br_events.csv')
        dividend_usd_events = pd.read_csv(f'{csv_directory}/dividend_usd_events.csv')
        valuation_events = pd.read_csv(f'{csv_directory}/valuation_events.csv')
        send_money_events = pd.read_csv(f'{csv_directory}/send_money_events.csv')
        dividend_distribution_events = pd.read_csv(f'{csv_directory}/dividend_distribution_events.csv')
        transfer_events = pd.read_csv(f'{csv_directory}/transfer_events.csv')

        # Funções de criação de eventos mapeadas
        event_creators = {
            'subscription': create_subscription_event,
            'create_property_invest_br_event': create_property_invest_br_event,
            'create_property_divest_br_event': create_property_divest_br_event,  
            'tax_pay': create_tax_pay_event, 
            'create_or_update_asset_create_historical_price_create_invest_br_event': create_or_update_asset_create_historical_price_create_invest_br_event,
            'create_or_update_asset_create_historical_price_create_invest_us_event': create_or_update_asset_create_historical_price_create_invest_us_event,
            'create_divest_br_event': create_divest_br_event,
            'create_divest_us_event': create_divest_us_event,
            'dividend_br': create_dividend_br_event,
            'dividend_usd': create_dividend_usd_event,
            'valuation': create_valuation_event,
            'send_money': send_money_event,
            'dividend_distribution': create_dividend_distribution_event,
            'transfer': create_transfer_event
        }

        # Função auxiliar para criar lista de eventos a partir de um DataFrame
        def create_event_list(df, event_type):
            event_list = []
            for index, row in df.iterrows():
                event = row.to_dict()
                event['type'] = event_type
                event['portfolio_id'] = self.portfolio_id  # Adiciona o ID do portfólio a todos os eventos
                event_list.append(event)
            return event_list

        # Criando listas de eventos a partir dos DataFrames
        subscription_list = create_event_list(subscription_events, 'subscription')
        invest_br_properties_list = create_event_list(property_invest_br_events, 'create_property_invest_br_event')
        divest_br_properties_list = create_event_list(property_divest_br_events, 'create_property_divest_br_event')
        tax_pay_list = create_event_list(tax_pay_events, 'tax_pay')
        invest_br_list = create_event_list(invest_br_events, 'create_or_update_asset_create_historical_price_create_invest_br_event')
        invest_usd_list = create_event_list(invest_usd_events, 'create_or_update_asset_create_historical_price_create_invest_us_event')
        divest_br_list = create_event_list(divest_br_events, 'create_divest_br_event')
        divest_usd_list = create_event_list(divest_usd_events, 'create_divest_usd_event')
        dividend_br_list = create_event_list(dividend_br_events, 'dividend_br')
        dividend_usd_list = create_event_list(dividend_usd_events, 'dividend_usd')
        valuation_list = create_event_list(valuation_events, 'valuation')
        send_money_list = create_event_list(send_money_events, 'send_money')
        dividend_distribution_list = create_event_list(dividend_distribution_events, 'dividend_distribution')
        transfer_list = create_event_list(transfer_events, 'transfer')

        # Combinando todas as listas de eventos
        events_list = (
                    subscription_list + 
                    invest_br_properties_list +
                    divest_br_properties_list +
                    tax_pay_list +
                    invest_br_list +
                    invest_usd_list +
                    divest_br_list + 
                    divest_usd_list +
                    dividend_br_list + 
                    dividend_usd_list +
                    valuation_list  +
                    send_money_list +
                    dividend_distribution_list +
                    transfer_list
                    )

        # Definindo intervalos de datas para os lotes
        date_ranges = [
            # testes
            # ("8_2019", datetime.strptime('2019-08-01', '%Y-%m-%d'), datetime.strptime('2019-08-31', '%Y-%m-%d')),
            # ("9_2019", datetime.strptime('2019-09-01', '%Y-%m-%d'), datetime.strptime('2019-09-30', '%Y-%m-%d')),
            # valendo mas comentado para os testes serem em periodos menores.
            ("2006", datetime.strptime('2006-01-01', '%Y-%m-%d'), datetime.strptime('2006-12-31', '%Y-%m-%d')),
            ("2007_2018", datetime.strptime('2007-01-01', '%Y-%m-%d'), datetime.strptime('2018-12-31', '%Y-%m-%d')),
            ("2019", datetime.strptime('2019-01-01', '%Y-%m-%d'), datetime.strptime('2019-12-31', '%Y-%m-%d')),
            # ("2020", datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-12-31', '%Y-%m-%d')),
            # ("2021", datetime.strptime('2021-01-01', '%Y-%m-%d'), datetime.strptime('2021-12-31', '%Y-%m-%d')),
            # ("2022", datetime.strptime('2022-01-01', '%Y-%m-%d'), datetime.strptime('2022-12-31', '%Y-%m-%d')),
            # ("2023", datetime.strptime('2023-01-01', '%Y-%m-%d'), datetime.strptime('2023-12-31', '%Y-%m-%d')),
            # ("1_2024_6_2024", datetime.strptime('2024-01-01', '%Y-%m-%d'), datetime.strptime('2024-06-30', '%Y-%m-%d')),
            # ("7_2024", datetime.strptime('2024-07-01', '%Y-%m-%d'), datetime.strptime('2024-07-31', '%Y-%m-%d')),

        ]

        # Ordenando a lista de eventos pela data
        for event in events_list:
            date_str = event.get('transaction_date') or event.get('pay_date') or event.get('record_date') or event.get('trade_date') or event.get('transfer_date')
            event['sort_date'] = convert_to_datetime(date_str)

        # Dividindo eventos em lotes e nomeando os lotes
        batches = {name: split_events_by_date(events_list, [(start_date, end_date)]) for name, start_date, end_date in date_ranges}

        # Lendo os lotes processados
        processed_batches = read_processed_batches()

        # Processando cada lote separadamente
        for batch_name, batch_list in batches.items():
            if batch_name in processed_batches:
                print(f'Skipping already processed batch: {batch_name}')
                continue
            
            error_log.clear()  # Limpa o log de erros antes de processar o próximo lote
            for batch in batch_list:
                batch.sort(key=lambda x: x['sort_date'])
                for event in batch:
                    event_without_type = {k: v for k, v in event.items() if k != 'type' and k != 'sort_date'}
                    try:
                        event_creators[event['type']](**event_without_type)
                    except Exception as e:
                        log_error(f'Error processing event: {str(e)}', event['type'], event['sort_date'])
            
            # Escrevendo erros em um arquivo CSV para o lote atual
            write_error_log_to_csv(error_log, batch_name)
            
            # Marcando o lote como processado
            write_processed_batch(batch_name)
