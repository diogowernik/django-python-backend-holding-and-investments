from django.db import models
from portfolios.models import Portfolio
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from cashflow.models import CurrencyTransaction
from timewarp.models import AssetHistoricalPrice, CurrencyHistoricalPrice
from trade.models import Trade
from brokers.models import Broker
from investments.models import Asset

class QuotaHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    event_type = models.CharField( 
        max_length=20,
        choices=[
            ('deposit', 'deposit'),
            ('withdraw', 'withdraw'),
            ('valuation', 'valuation'),
            ('dividend receive', 'dividend receive'),
            ('dividend payment', 'dividend payment'),
            ('invest br', 'invest br'),
        ],
        default='deposit'
    )
    # tem que considerar a cotação do dolar do dia
    value_brl = models.FloatField(default=0) # Exemplo: 1000 reais
    value_usd = models.FloatField(default=0) # Exemplo: 200 dolares (200 * 5 = 1000 reais)
    # Calculado Automaticamente
    date = models.DateTimeField(default=datetime.now, editable=False) # sempre vai ser uma foto do momento, gravado em pedra.
    total_brl = models.FloatField(default=0, editable=False)
    total_usd = models.FloatField(default=0, editable=False)
    quota_amount = models.FloatField(default=0, editable=False)
    quota_price_brl = models.FloatField(default=0, editable=False)
    quota_price_usd = models.FloatField(default=0, editable=False)
    percentage_change = models.FloatField(default=0, editable=False)

class SubscriptionEvent(CurrencyTransaction):
    def __init__(self, *args, **kwargs):
        super(SubscriptionEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'deposit'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit' # deixar hidden no admin e frontend
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd

        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            quota_amount = last_quota_history.quota_amount + (value_brl / last_quota_history.quota_price_brl) if last_quota_history.quota_price_brl != 0 else 0
            quota_price_brl = total_brl / quota_amount if quota_amount != 0 else 0
            quota_price_usd = quota_price_brl * value_usd / value_brl if value_brl != 0 else 0 
            percentage_change = quota_price_brl * ((quota_price_brl / last_quota_history.quota_price_brl) - 1) if last_quota_history.quota_price_brl != 0 else 0
        else:
            total_brl = value_brl
            total_usd = value_usd
            quota_amount = value_brl
            quota_price_brl = 1
            quota_price_usd = value_usd / value_brl if value_brl != 0 else 0
            percentage_change = 0
        
        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='deposit',
            value_brl=value_brl,
            value_usd=value_usd,
            total_brl=total_brl,
            total_usd=total_usd,
            quota_amount=quota_amount,
            quota_price_brl=quota_price_brl,
            quota_price_usd=quota_price_usd,
            percentage_change=percentage_change,            
        )
  
class DividendReceiveEvent(CurrencyTransaction):
    # Campos herdados de CurrencyTransaction:
    # portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    # transaction_date = models.DateTimeField(default=datetime.now)
    # transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='buy')
    # transaction_amount = models.FloatField(default=0)
    # price_brl = models.FloatField(default=0)
    # price_usd = models.FloatField(default=0)
    
    def __init__(self, *args, **kwargs):
        super(DividendReceiveEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'deposit'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit'
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd

        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            # The amount of quotas stays the same
            quota_amount = last_quota_history.quota_amount
            
            # The price per quota increases
            quota_price_brl = total_brl / quota_amount
            quota_price_usd = total_usd / quota_amount
            
            percentage_change = (quota_price_brl / last_quota_history.quota_price_brl) - 1

            # Create a new QuotaHistory
            QuotaHistory.objects.create(
                portfolio=self.portfolio,
                date=self.transaction_date,
                event_type='dividend receive',
                value_brl=value_brl,
                value_usd=value_usd,
                total_brl=total_brl,
                total_usd=total_usd,
                quota_amount=quota_amount,
                quota_price_brl=quota_price_brl,
                quota_price_usd=quota_price_usd,
                percentage_change=percentage_change,
            )
        else:
            # Error message
            raise Exception('Não há histórico de cotas para este portfolio, por isso voce não pode receber dividendos.')

class ValuationEvent(QuotaHistory):
    @transaction.atomic
    def save(self, *args, **kwargs):
        self.event_type = 'valuation'
        self.value_brl = 0  # Assegura que o valor em reais é sempre 0
        self.value_usd = 0  # Assegura que o valor em dólares é sempre 0
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            # A quantidade de cotas permanece a mesma
            self.quota_amount = last_quota_history.quota_amount

            # O preço por cota muda devido à avaliação do ativo
            self.quota_price_brl = total_brl / self.quota_amount if self.quota_amount != 0 else 0
            self.quota_price_usd = total_usd / self.quota_amount if self.quota_amount != 0 else 0

            self.percentage_change = (self.quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0

            self.total_brl = total_brl
            self.total_usd = total_usd

        else:
            # Mensagem de erro
            raise Exception('Não há histórico de cotas para este portfolio, por isso voce não pode afirmar a avaliação dos ativos.')



class RedemptionEvent(CurrencyTransaction):
    def __init__(self, *args, **kwargs):
        super(RedemptionEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'withdraw'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            quota_amount = last_quota_history.quota_amount + (value_brl / last_quota_history.quota_price_brl) if last_quota_history.quota_price_brl != 0 else 0
            quota_price_brl = total_brl / quota_amount if quota_amount != 0 else 0
            quota_price_usd = total_usd / quota_amount if quota_amount != 0 else 0
            percentage_change = (quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0
        else:
            # Error message
            raise Exception('Não há histórico de cotas para este portfolio, por isso voce não pode resgatar.')

        # Create a new QuotaHistory
        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='withdraw',
            value_brl=value_brl,
            value_usd=value_usd,
            total_brl=total_brl,
            total_usd=total_usd,
            quota_amount=quota_amount,
            quota_price_brl=quota_price_brl,
            quota_price_usd=quota_price_usd,
            percentage_change=percentage_change,            
        )
  
class DividendPayEvent(CurrencyTransaction):
    def __init__(self, *args, **kwargs):
        super(DividendPayEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'withdraw'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            # The amount of quotas stays the same
            quota_amount = last_quota_history.quota_amount

            # The price per quota decreases
            quota_price_brl = total_brl / quota_amount if quota_amount != 0 else 0
            quota_price_usd = total_usd / quota_amount if quota_amount != 0 else 0

            percentage_change = (quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0

            # Create a new QuotaHistory
            QuotaHistory.objects.create(
                portfolio=self.portfolio,
                date=self.transaction_date,
                event_type='dividend payment',
                value_brl=value_brl,
                value_usd=value_usd,
                total_brl=total_brl,
                total_usd=total_usd,
                quota_amount=quota_amount,
                quota_price_brl=quota_price_brl,
                quota_price_usd=quota_price_usd,
                percentage_change=percentage_change,
            )
        else:
            # Error message
            raise Exception('Não há histórico de cotas para este portfolio, por isso voce não pode pagar dividendos.')

class InvestBrEvent(CurrencyTransaction):
    to_broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_amount = models.FloatField(default=0)
    asset_price_brl = models.FloatField(default=0)

    def __init__(self, *args, **kwargs):
        super(InvestBrEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'withdraw'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        trade = self.create_trade()
        self.transaction_amount = (trade.trade_amount * trade.price_brl) 
        super().save(*args, **kwargs)
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 

    def create_trade(self):
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            broker=self.to_broker,
            trade_amount=self.trade_amount,
            trade_date=self.transaction_date,
            trade_type='buy',
        )
        return trade

    def create_portfolio_history(self):
        portfolio_history = PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        total_brl = portfolio_history.total_brl  
        total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            # The amount of quotas stays the same
            quota_amount = last_quota_history.quota_amount

            # The price per quota decreases
            quota_price_brl = total_brl / quota_amount if quota_amount != 0 else 0
            quota_price_usd = total_usd / quota_amount if quota_amount != 0 else 0

            percentage_change = (quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0

            # Create a new QuotaHistory
            QuotaHistory.objects.create(
                portfolio=self.portfolio,
                date=self.transaction_date,
                event_type='invest br',
                value_brl=value_brl,
                value_usd=value_usd,
                total_brl=total_brl,
                total_usd=total_usd,
                quota_amount=quota_amount,
                quota_price_brl=quota_price_brl,
                quota_price_usd=quota_price_usd,
                percentage_change=percentage_change,
            )
        else:
            # Error message
            raise Exception('Não há histórico de cotas para este portfolio, por isso voce não pode pagar dividendos.')





class PortfolioHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date = models.DateField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()

    def __str__(self):
        return f'{self.portfolio.name} - {self.date}'

    class Meta:
        verbose_name_plural = 'Histórico de Portfolios'

    def get_transactions_totals(self, investment):
        buy_trades = Trade.objects.filter(
            portfolio_investment=investment,
            trade_type='buy',
            trade_date__lte=self.date
        ).aggregate(Sum('trade_amount'))['trade_amount__sum'] or 0

        sell_trades = Trade.objects.filter(
            portfolio_investment=investment,
            trade_type='sell',
            trade_date__lte=self.date
        ).aggregate(Sum('trade_amount'))['trade_amount__sum'] or 0

        deposits = CurrencyTransaction.objects.filter(
            portfolio_investment=investment,
            transaction_type='deposit',
            transaction_date__lte=self.date
        ).aggregate(Sum('transaction_amount'))['transaction_amount__sum'] or 0

        withdraws = CurrencyTransaction.objects.filter(
            portfolio_investment=investment,
            transaction_type='withdraw',
            transaction_date__lte=self.date
        ).aggregate(Sum('transaction_amount'))['transaction_amount__sum'] or 0

        return buy_trades, sell_trades, deposits, withdraws

    def get_historical_price_and_exchange_rate(self, investment, currency_pair):
        try:
            historical_price = AssetHistoricalPrice.objects.filter(
                asset=investment.asset,
                date__lte=self.date,
            ).latest('date')
        except AssetHistoricalPrice.DoesNotExist:
            historical_price = None

        try:
            exchange_rate = CurrencyHistoricalPrice.objects.filter(
                currency_pair=currency_pair, 
                date__lte=self.date  
            ).latest('date')
            print(exchange_rate) 
        except CurrencyHistoricalPrice.DoesNotExist:
            exchange_rate = None

        return historical_price, exchange_rate

    def calculate_total_values(self, investment, historical_price, exchange_rate):
        total_brl = 0
        total_usd = 0

        if historical_price:
            if investment.broker.main_currency.ticker == 'BRL':
                total_brl += historical_price.close * investment.shares_amount
                if exchange_rate:
                    total_usd += (historical_price.close * investment.shares_amount) / exchange_rate.close
            elif investment.broker.main_currency.ticker == 'USD':
                total_usd += historical_price.close * investment.shares_amount
                if exchange_rate:
                    total_brl += (historical_price.close * investment.shares_amount) * exchange_rate.close
        return total_brl, total_usd
    
    def save(self, *args, **kwargs):
        portfolio_investments = self.portfolio.portfolioinvestment_set.all()

        total_brl = 0
        total_usd = 0

        for investment in portfolio_investments:
            buy_trades, sell_trades, deposits, withdraws = self.get_transactions_totals(investment)

            if buy_trades - sell_trades + deposits - withdraws > 0:
                currency_pair = 'BRLUSD' if investment.broker.main_currency == 'BRL' else 'USDBRL'
                historical_price, exchange_rate = self.get_historical_price_and_exchange_rate(investment, currency_pair)

                total_brl_investment, total_usd_investment = self.calculate_total_values(investment, historical_price, exchange_rate)

                total_brl += total_brl_investment
                total_usd += total_usd_investment

        self.total_brl = total_brl
        self.total_usd = total_usd

        super().save(*args, **kwargs)

