# event_creators.py
from datetime import timedelta
from equity.models import SubscriptionEvent, InvestBrEvent, TaxPayEvent, DividendReceiveEvent, DivestBrEvent, InvestUsEvent, DivestUsEvent, ValuationEvent, SendMoneyEvent, DividendDistributionEvent
from portfolios.models import Portfolio
from brokers.models import Broker
from investments.models import Asset
from dividends.models import DividendBr, DividendUs
from cashflow.models import CurrencyTransfer
from categories.models import Category, SubCategory
from timewarp.models import AssetHistoricalPrice
from .utils import log_error, convert_to_datetime
# ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

def create_valuation_event(portfolio_id, transaction_date):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    date = convert_to_datetime(transaction_date)
    ValuationEvent.objects.create(
        portfolio=portfolio,
        date=date
    )
    print(f'Successfully created ValuationEvent for Portfolio ID {portfolio_id} on {date}')

# brl 
def create_subscription_event(portfolio_id, broker_name, transaction_date, transaction_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    SubscriptionEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        transaction_amount=transaction_amount # brl
    )
    print(f'Successfully created SubscriptionEvent for Portfolio ID {portfolio} on {transaction_date}')

def create_dividend_distribution_event(portfolio_id, broker_name, transaction_date, transaction_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    DividendDistributionEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        transaction_amount=transaction_amount
    )
    print(f'Successfully created DividendDistributionEvent for Portfolio ID {portfolio} on {transaction_date}')

# brl
def create_tax_pay_event(portfolio_id, broker, transaction_date, transaction_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker)
    TaxPayEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        transaction_amount=transaction_amount
    )
    print('Successfully created TaxPayEvent')

# brl
def create_dividend_br_event(asset_ticker, record_date, value_per_share_brl, pay_date, portfolio_id):
    try:
        asset = Asset.objects.get(ticker=asset_ticker)
        DividendBr.objects.create(
            asset=asset,
            value_per_share_brl=value_per_share_brl,
            record_date=record_date,
            pay_date=pay_date
        )
        print(f'Successfully created Dividend for {asset.ticker} on {pay_date}')
    except Asset.DoesNotExist:
        log_error(f'Error: Asset with ticker {asset_ticker} does not exist')

#usd 
def create_dividend_usd_event(asset_ticker, record_date, value_per_share_usd, pay_date, portfolio_id):
    try:
        asset = Asset.objects.get(ticker=asset_ticker)
    except Asset.DoesNotExist:
        log_error(f'Error: Asset with ticker {asset_ticker} does not exist')
        return  # Pular a criação do dividendo

    # Converte `record_date` e `pay_date` para objetos datetime, se necessário
    record_date = convert_to_datetime(record_date)
    pay_date = convert_to_datetime(pay_date)
    
    DividendUs.objects.create(
        asset=asset,
        value_per_share_usd=value_per_share_usd,
        record_date=record_date,
        pay_date=pay_date
    )
    print(f'Successfully created Dividend for {asset.ticker} on {pay_date.strftime("%Y-%m-%d")}')

    
# brl and usd - Verify
def create_dividend_receive_event(portfolio_id, broker_name, transaction_date, transaction_amount, asset_ticker):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    DividendReceiveEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        transaction_amount=transaction_amount
    )
    print(f'Successfully created DividendReceiveEvent for Portfolio ID {portfolio_id} on {transaction_date}')

# brl and usd
def create_transfer_event(portfolio_id, from_broker_name, to_broker_name, transfer_date, transfer_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    from_broker = Broker.objects.get(name=from_broker_name)
    to_broker = Broker.objects.get(name=to_broker_name)
    CurrencyTransfer.objects.create(
        portfolio=portfolio,
        from_broker=from_broker,
        to_broker=to_broker,
        transfer_date=transfer_date,
        transfer_amount=transfer_amount
    )
    print('Successfully created TransferEvent')

# brl and usd
def create_or_update_asset(category_id, subcategory_id, ticker, price_usd, price_brl):
    try:
        # Tentando obter o objeto BrStocks pelo ticker
        asset = Asset.objects.get(ticker=ticker)
        
        # Atualizando os valores se o objeto for encontrado
        asset.price_usd = price_usd
        asset.price_brl = price_brl
        asset.save()
        
        print(f'Successfully updated BrStock with ticker {ticker}')
        
    except ObjectDoesNotExist:
        # Se o objeto não for encontrado, um novo será criado
        category = Category.objects.get(id=category_id)
        subcategory = SubCategory.objects.get(id=subcategory_id)
        
        Asset.objects.create(
            category=category,
            subcategory=subcategory,
            ticker=ticker,
            price_usd=price_usd,
            price_brl=price_brl
        )
        
        print(f'Successfully created BrStock with ticker {ticker}')

# brl
def create_asset_historical_price_brl(asset_ticker, price_brl, date):
    asset = Asset.objects.get(ticker=asset_ticker)
    date = convert_to_datetime(date) 
    date = date - timedelta(days=1)
    
    AssetHistoricalPrice.objects.create(
        asset=asset,
        currency="BRL",
        date=date,
        open=price_brl,
        high=price_brl,
        low=price_brl,
        close=price_brl
    )
    print(f'Successfully created AssetPriceHistory for {asset.ticker} on {date}')

# usd
def create_asset_historical_price_usd(asset_ticker, price_usd, date):
    asset = Asset.objects.get(ticker=asset_ticker)
    date = convert_to_datetime(date)
    date = date - timedelta(days=1)
    
    AssetHistoricalPrice.objects.create(
        asset=asset,
        currency="USD",
        date=date,
        open=price_usd,
        high=price_usd,
        low=price_usd,
        close=price_usd
    )
    print(f'Successfully created AssetPriceHistory for {asset.ticker} on {date}')

# brl
def create_invest_br_event(portfolio_id, broker_name, transaction_date, asset_ticker, trade_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    
    asset = Asset.objects.get(ticker=asset_ticker)
    asset_price_brl = asset.price_brl
    InvestBrEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        to_broker=broker, # to_broker_name e broker_name são o mesmo
        asset=asset,
        trade_amount=trade_amount,
        asset_price_brl=asset_price_brl
    )
    print(f'Successfully created InvestBrEvent for Portfolio ID {portfolio_id} on {transaction_date}')

def create_property_invest_br_event(portfolio_id, broker_name, transaction_date, to_broker_name, asset_ticker, trade_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    to_broker = Broker.objects.get(name=to_broker_name)
    asset = Asset.objects.get(ticker=asset_ticker)
    InvestBrEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        to_broker=to_broker,
        asset=asset,
        trade_amount=trade_amount
    )
    print('Successfully created InvestBrEvent')

def create_property_divest_br_event(portfolio_id, broker_name, transaction_date, to_broker_name, asset_ticker, trade_amount, asset_price_brl):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    to_broker = Broker.objects.get(name=to_broker_name)
    asset = Asset.objects.get(ticker=asset_ticker)
    DivestBrEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        to_broker=to_broker,
        asset=asset,
        trade_amount=trade_amount,
        asset_price_brl=asset_price_brl
    )
    print('Successfully created DivestBrEvent')

# usd
def create_invest_usd_event(portfolio_id, broker_name, transaction_date, asset_ticker, trade_amount):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    
    asset = Asset.objects.get(ticker=asset_ticker)
    asset_price_usd = asset.price_usd
    InvestUsEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=transaction_date,
        asset=asset,
        trade_amount=trade_amount,
        asset_price_usd=asset_price_usd
    )
    print(f'Successfully created InvestUsEvent for Portfolio ID {portfolio_id} on {transaction_date}')

def create_or_update_asset_create_historical_price_create_invest_br_event(
    category_name, subcategory_name, ticker, price_usd, price_brl,
    trade_date, portfolio_id, broker_name, trade_amount
):
    
    try:
        subcategory_id = SubCategory.objects.get(name=subcategory_name).id
    except SubCategory.DoesNotExist:
        log_error(f'SubCategory "{subcategory_name}" does not exist, using default ID 1')
        subcategory_id = 1
    
    try:
        category_id = Category.objects.get(name=category_name).id
    except Category.DoesNotExist:
        log_error(f'Category "{category_name}" does not exist, using default ID 1')
        category_id = 1
    
    # Primeiro, criamos ou atualizamos o ativo
    create_or_update_asset(category_id, subcategory_id, ticker, price_usd, price_brl)

    # Em seguida, criamos o preço histórico do ativo
    create_asset_historical_price_brl(ticker, price_brl, trade_date)

    # Por último, criamos o evento InvestBr
    create_invest_br_event(portfolio_id, broker_name, trade_date, ticker, trade_amount)
    
    print(f'Successfully executed all actions for ticker {ticker}')

# usd
def create_or_update_asset_create_historical_price_create_invest_us_event(
    category_name, subcategory_name, ticker, price_usd, price_brl,
    trade_date, portfolio_id, broker_name, trade_amount
):
    
    try:
        subcategory_id = SubCategory.objects.get(name=subcategory_name).id
    except SubCategory.DoesNotExist:
        log_error(f'SubCategory "{subcategory_name}" does not exist, using default ID 1')
        subcategory_id = 1
    
    try:
        category_id = Category.objects.get(name=category_name).id
    except Category.DoesNotExist:
        log_error(f'Category "{category_name}" does not exist, using default ID 1')
        category_id = 1
    
    # Primeiro, criamos ou atualizamos o ativo
    create_or_update_asset(category_id, subcategory_id, ticker, price_usd, price_brl)

    # Em seguida, criamos o preço histórico do ativo
    create_asset_historical_price_usd(ticker, price_usd, trade_date)

    # Por último, criamos o evento InvestUs
    create_invest_usd_event(portfolio_id, broker_name, trade_date, ticker, trade_amount)
    
    print(f'Successfully executed all actions for ticker {ticker}')


# brl
def create_divest_br_event(portfolio_id, broker_name, trade_date, ticker, trade_amount, price_brl, price_usd):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    
    asset = Asset.objects.get(ticker=ticker)
    DivestBrEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        to_broker=broker,
        transaction_date=trade_date,
        asset=asset,
        trade_amount=trade_amount,
        asset_price_brl=price_brl
    )
    print(f'Successfully created DivestBrEvent for Portfolio ID {portfolio_id} on {trade_date}')

# usd
def create_divest_us_event(portfolio_id, broker_name, trade_date, ticker, trade_amount, price_usd, price_brl):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    broker = Broker.objects.get(name=broker_name)
    
    try:
        asset = Asset.objects.get(ticker=ticker)
    except Asset.DoesNotExist:
        log_error(f'Error: Asset with ticker {ticker} does not exist for DivestUsEvent on {trade_date}')
        return
    
    DivestUsEvent.objects.create(
        portfolio=portfolio,
        broker=broker,
        transaction_date=trade_date,
        asset=asset,
        trade_amount=trade_amount,
        asset_price_usd=price_usd
    )
    print(f'Successfully created DivestUsEvent for Portfolio ID {portfolio_id} on {trade_date}')

def send_money_event(portfolio_id, from_broker_name, to_broker_name, transfer_date, from_transfer_amount, exchange_rate):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    from_broker = Broker.objects.get(name=from_broker_name)
    to_broker = Broker.objects.get(name=to_broker_name)
    try:
        SendMoneyEvent.objects.create(
            portfolio=portfolio,
            from_broker=from_broker,
            to_broker=to_broker,
            transfer_date=transfer_date,
            from_transfer_amount=from_transfer_amount,
            exchange_rate=exchange_rate
        )
        print(f'Successfully created SendMoneyEvent for Portfolio ID {portfolio_id} on {transfer_date}')
    except Exception as e:
        log_error(f'Error: {e}')
