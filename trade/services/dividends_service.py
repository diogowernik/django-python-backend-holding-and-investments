
from django.apps import apps

def update_portfolio_dividend(trade_history):
    PortfolioDividend = apps.get_model('dividends', 'PortfolioDividend')

    portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=trade_history.portfolio_investment)

    for portfolio_dividend in portfolio_dividends:
        transaction_data = trade_history.get_transaction_data(portfolio_dividend.record_date)
        update_portfolio_dividend_record(trade_history, portfolio_dividend, transaction_data)

def update_portfolio_dividend_fields(trade_history, portfolio_dividend, transaction_data):
    total_shares, average_price_brl, average_price_usd = transaction_data

    portfolio_dividend.shares_amount = total_shares
    portfolio_dividend.average_price_brl = average_price_brl
    portfolio_dividend.average_price_usd = average_price_usd
    portfolio_dividend.save()

def update_portfolio_dividend_record(trade_history, portfolio_dividend, transaction_data):
    update_portfolio_dividend_fields(trade_history, portfolio_dividend, transaction_data)

def create_portfolio_dividend(trade_history):
    Dividend = apps.get_model('dividends', 'Dividend') 

    dividends = Dividend.objects.filter(
        asset=trade_history.portfolio_investment.asset, 
        record_date__gte=trade_history.trade_date
    )

    for dividend in dividends:
        transaction_data = trade_history.get_transaction_data(dividend.record_date)
        create_or_update_portfolio_dividend(trade_history, dividend, transaction_data)


def create_or_update_portfolio_dividend(trade_history, dividend, transaction_data):
    PortfolioDividend = apps.get_model('dividends', 'PortfolioDividend') 
    total_shares, average_price_brl, average_price_usd = transaction_data

    portfolio_dividend, created = PortfolioDividend.objects.get_or_create(
        portfolio_investment=trade_history.portfolio_investment,
        dividend=dividend,
        defaults={
            'trade_history': trade_history,
            'shares_amount': total_shares, 
            'average_price_brl': average_price_brl,
            'average_price_usd': average_price_usd,
            'asset': dividend.asset,
            'category': dividend.asset.category,
            'record_date': dividend.record_date,
            'pay_date': dividend.pay_date,
            'value_per_share_brl': dividend.value_per_share_brl,
            'value_per_share_usd': dividend.value_per_share_usd,
        }
    )
    if not created:
        update_portfolio_dividend_fields(trade_history, portfolio_dividend, transaction_data)

