from cashflow.models import CurrencyTransaction

# Create or update a currency transaction related to the trade
def create_or_update_currency_transaction(trade):
    currency_transaction_type = 'withdraw' if trade.transaction_type == 'buy' else 'deposit'
    currency_transaction_amount = get_currency_transaction_amount(trade)

    currency_transaction, created = CurrencyTransaction.objects.get_or_create(
        portfolio=trade.portfolio,
        broker=trade.broker,
        transaction_date=trade.transaction_date,
        defaults={
            'transaction_type': currency_transaction_type,
            'transaction_amount': currency_transaction_amount,
            'price_brl': trade.price_brl,
            'price_usd': trade.price_usd,
        }
    )

    if not created:
        currency_transaction.transaction_type = currency_transaction_type
        currency_transaction.transaction_amount = currency_transaction_amount
        currency_transaction.price_brl = trade.price_brl
        currency_transaction.price_usd = trade.price_usd
        currency_transaction.save()

# Get the total amount of currency involved in the trade
def get_currency_transaction_amount(trade):
    if trade.broker.main_currency.ticker == 'BRL':
        return trade.transaction_amount * trade.price_brl
    elif trade.broker.main_currency.ticker == 'USD':
        return trade.transaction_amount * trade.price_usd

# Delete the currency transaction related to the trade
def delete_currency_transaction(trade):
    try:
        currency_transaction = CurrencyTransaction.objects.get(
            portfolio=trade.portfolio,
            broker=trade.broker,
            transaction_date=trade.transaction_date
        )
        currency_transaction.delete()
    except CurrencyTransaction.DoesNotExist:
        pass
