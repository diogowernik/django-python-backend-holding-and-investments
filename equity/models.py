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
    # Campos herdados de CurrencyTransaction:
    # portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    # transaction_date = models.DateTimeField(default=datetime.now)
    # transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='deposit')
    # transaction_amount = models.FloatField(default=0)
    # price_brl = models.FloatField(default=0)
    # price_usd = models.FloatField(default=0)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
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

class RedemptionEvent(CurrencyTransaction):
    # Campos herdados de CurrencyTransaction:
    # portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    # transaction_date = models.DateTimeField(default=datetime.now)
    # transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='deposit')
    # transaction_amount = models.FloatField(default=0)
    # price_brl = models.FloatField(default=0)
    # price_usd = models.FloatField(default=0)

    @transaction.atomic
    def save(self, *args, **kwargs):
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
    
