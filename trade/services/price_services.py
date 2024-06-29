
from timewarp.models import CurrencyHistoricalPrice, AssetHistoricalPrice
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime

# set_prices when fields price_brl and price_usd are null or not set
def set_prices(trade):
    set_price(trade, trade.asset.ticker, 'BRL') # price_brl
    set_price(trade, trade.asset.ticker, 'USD') # price_usd

# set_price for set_prices
def set_price(trade, asset_ticker, target_currency):
    price_attribute = f'price_{target_currency.lower()}'
    if getattr(trade, price_attribute) is None:
        today = datetime.today().strftime('%Y-%m-%d')
        trade_date = trade.trade_date
        if trade_date == today:
            setattr(trade, price_attribute, getattr(trade.asset, price_attribute))
        elif trade_date < today:
            set_historical_price(trade, asset_ticker, target_currency, trade_date, price_attribute)

# set_historical_price for set_price
def set_historical_price(trade, asset_ticker, target_currency, trade_date, price_attribute):
    try:
        asset_historical_price = AssetHistoricalPrice.objects.filter(
            asset__ticker=asset_ticker, 
            date__lte=trade_date  # Obter o último preço registrado antes ou na data da transação
        ).latest('date')  # Ordenar em ordem decrescente de data e pegar o primeiro (o mais recente)

        historical_price_currency = asset_historical_price.currency

        if historical_price_currency == target_currency:
            setattr(trade, price_attribute, asset_historical_price.close)
        else:
            set_converted_price(trade, asset_historical_price, historical_price_currency, target_currency, trade_date, price_attribute)
    except ObjectDoesNotExist:
        raise ValidationError(f'Não foi possível encontrar o preço do ativo {asset_ticker} na data {trade_date}')


# set_converted_price for set_historical_price
def set_converted_price(trade, asset_historical_price, historical_price_currency, target_currency, trade_date, price_attribute):
    currency_historical_price = CurrencyHistoricalPrice.objects.filter(
        currency_pair=f'{historical_price_currency}{target_currency}',
        date__lte=trade_date
    ).latest('date')

    if currency_historical_price:
        converted_price = asset_historical_price.close * currency_historical_price.close
        setattr(trade, price_attribute, converted_price)
    else:
        raise ValidationError(f'Não foi possível encontrar a taxa de câmbio de {historical_price_currency} para {target_currency} na data {trade_date}')