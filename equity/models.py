from django.db import models
from portfolios.models import Portfolio
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from cashflow.models import CurrencyTransaction
from django.db.models import F

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
        self.create_quota_history()

    def create_quota_history(self):
        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd

        total_brl = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum']
        total_usd = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_usd'))['total_today_usd__sum']
        print(total_brl)

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.transaction_date).first()

        if last_quota_history:
            quota_amount = last_quota_history.quota_amount + (value_brl / last_quota_history.quota_price_brl) if last_quota_history.quota_price_brl != 0 else 0
            quota_price_brl = total_brl / quota_amount if quota_amount != 0 else 0
            quota_price_usd = total_usd / quota_amount if quota_amount != 0 else 0
            percentage_change = (quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0
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

class RedemptionEvent(CurrencyTransaction):
    def __init__(self, *args, **kwargs):
        super(RedemptionEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'withdraw'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)
        self.create_quota_history()

    def create_quota_history(self):
        value_brl = (self.transaction_amount * self.price_brl) * -1
        value_usd = (self.transaction_amount * self.price_usd) * -1

        total_brl = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum']
        total_usd = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_usd'))['total_today_usd__sum']

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
    
class DividendReceiveEvent(CurrencyTransaction):
    
    def __init__(self, *args, **kwargs):
        super(DividendReceiveEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'deposit'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit'
        super().save(*args, **kwargs)
        self.create_quota_history()

    def create_quota_history(self):
        # The increase in portfolio value due to received dividends
        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd

        # The new total portfolio value
        total_brl = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum']
        total_usd = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_usd'))['total_today_usd__sum']

        # Get the last quota history
        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.first()

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

class DividendPayEvent(CurrencyTransaction):
    
    def __init__(self, *args, **kwargs):
        super(DividendPayEvent, self).__init__(*args, **kwargs)
        self.transaction_type = 'withdraw'

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)
        self.create_quota_history()

    def create_quota_history(self):
        # The decrease in portfolio value due to paid dividends
        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        # The new total portfolio value
        total_brl = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum']
        total_usd = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_usd'))['total_today_usd__sum']

        # Get the last quota history
        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.first()

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

class AssetValuationEvent(QuotaHistory):
    @transaction.atomic
    def save(self, *args, **kwargs):
        self.event_type = 'valuation'
        self.value_brl = 0  # Assegura que o valor em reais é sempre 0
        self.value_usd = 0  # Assegura que o valor em dólares é sempre 0
        self.create_quota_history()
        super().save(*args, **kwargs)

    def create_quota_history(self):
        # O valor total do portfólio
        total_brl = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum']
        total_usd = self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_usd'))['total_today_usd__sum']

        # Pega o último registro de histórico de cota
        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.first()

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

