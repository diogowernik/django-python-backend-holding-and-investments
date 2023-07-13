
from timewarp.models import CurrencyHistoricalPrice, AssetHistoricalPrice
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime

# set_prices when fields price_brl and price_usd are null or not set
def set_prices(transaction):
    set_price(transaction, transaction.asset.ticker, 'BRL') # price_brl
    set_price(transaction, transaction.asset.ticker, 'USD') # price_usd

# set_price for set_prices
def set_price(transaction, asset_ticker, target_currency):
    price_attribute = f'price_{target_currency.lower()}'
    if getattr(transaction, price_attribute) is None:
        today = datetime.today().strftime('%Y-%m-%d')
        transaction_date = transaction.transaction_date.strftime('%Y-%m-%d')
        if transaction_date == today:
            setattr(transaction, price_attribute, getattr(transaction.asset, price_attribute))
        elif transaction_date < today:
            set_historical_price(transaction, asset_ticker, target_currency, transaction_date, price_attribute)

# set_historical_price for set_price
def set_historical_price(transaction, asset_ticker, target_currency, transaction_date, price_attribute):
    try:
        asset_historical_price = AssetHistoricalPrice.objects.get(
            asset__ticker=asset_ticker, 
            date=transaction_date
        )
        historical_price_currency = asset_historical_price.currency

        if historical_price_currency == target_currency:
            setattr(transaction, price_attribute, asset_historical_price.close)
        else:
            set_converted_price(transaction, asset_historical_price, historical_price_currency, target_currency, transaction_date, price_attribute)
    except ObjectDoesNotExist:
        raise ValidationError(f'Não foi possível encontrar o preço do ativo {asset_ticker} na data {transaction_date}')

# set_converted_price for set_historical_price
def set_converted_price(transaction, asset_historical_price, historical_price_currency, target_currency, transaction_date, price_attribute):
    currency_historical_price = CurrencyHistoricalPrice.objects.filter(
        currency_pair=f'{historical_price_currency}{target_currency}',
        date__lte=transaction_date
    ).latest('date')

    if currency_historical_price:
        converted_price = asset_historical_price.close * currency_historical_price.close
        setattr(transaction, price_attribute, converted_price)
    else:
        raise ValidationError(f'Não foi possível encontrar a taxa de câmbio de {historical_price_currency} para {target_currency} na data {transaction_date}')