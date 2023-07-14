from django.db import models
from portfolios.models import Portfolio

class QuotaHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date = models.DateField()
    total_quotas = models.FloatField()
    quota_price_brl = models.FloatField()
    quota_price_usd = models.FloatField()
    event_type = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.portfolio} - {self.date}'


class QuotaState(models.Model):
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    total_quotas = models.FloatField()
    quota_price_brl = models.FloatField()
    quota_price_usd = models.FloatField()

    def __str__(self):
        return f'{self.portfolio}'


class QuotaEvent(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date = models.DateField()
    EVENT_TYPES = [
        ('dividend_receive', 'Dividend Receive'),
        ('dividend_pay', 'Dividend Pay'),
        ('subscription', 'Subscription'),
        ('redemption', 'Redemption'),
        ('asset_valuation', 'Asset Valuation'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    new_total_quotas = models.FloatField()  # o novo total de cotas
    new_quota_price_brl = models.FloatField()
    new_quota_price_usd = models.FloatField()

    def __str__(self):
        return f'{self.portfolio} - {self.event_type} - {self.date}'
    
    def save(self, *args, **kwargs):
        self.apply()
        super().save(*args, **kwargs)
        self.update_portfolio_state()
        self.create_quota_history()

    def apply(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_portfolio_state(self):
        state = self.portfolio.quotastate
        state.total_quotas = self.new_total_quotas
        state.quota_price_brl = self.new_quota_price_brl
        state.quota_price_usd = self.new_quota_price_usd
        state.save()

    def create_quota_history(self):
        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.date,
            total_quotas=self.new_total_quotas,
            quota_price_brl=self.new_quota_price_brl,
            quota_price_usd=self.new_quota_price_usd,
            event_type=self.event_type
        )

class DividendReceiveEvent(QuotaEvent):
    total_dividends_brl = models.FloatField()
    total_dividends_usd = models.FloatField()
    
    def apply(self):
        # Increase the quota price as the portfolio value increases due to received dividends
        self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl + self.total_dividends_brl / self.portfolio.quotastate.total_quotas
        self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd + self.total_dividends_usd / self.portfolio.quotastate.total_quotas

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_type = 'dividend_receive'

class DividendPayEvent(QuotaEvent):
    total_dividends_brl = models.FloatField()
    total_dividends_usd = models.FloatField()

    def apply(self):
        # Decrease the quota price as the portfolio value decreases due to paid dividends
        self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl - self.total_dividends_brl / self.portfolio.quotastate.total_quotas
        self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd - self.total_dividends_usd / self.portfolio.quotastate.total_quotas

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_type = 'dividend_pay'

class SubscriptionEvent(QuotaEvent):
    paid_amount_brl = models.FloatField()  # the amount of money used to buy new quotas
    paid_amount_usd = models.FloatField()

    def apply(self):
        # Increase the total quotas and adjust the quota price
        current_state = self.portfolio.quotastate
        new_total_value_brl = current_state.total_quotas * current_state.quota_price_brl + self.paid_amount_brl
        new_total_value_usd = current_state.total_quotas * current_state.quota_price_usd + self.paid_amount_usd
        self.new_total_quotas = current_state.total_quotas + self.paid_amount_brl / current_state.quota_price_brl  # assuming quota price is in BRL
        self.new_quota_price_brl = new_total_value_brl / self.new_total_quotas
        self.new_quota_price_usd = new_total_value_usd / self.new_total_quotas
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_type = 'subscription'

class RedemptionEvent(QuotaEvent):
    sold_quotas = models.FloatField()  # the amount of quotas sold

    def apply(self):
        # Decrease the total quotas and adjust the quota price
        current_state = self.portfolio.quotastate
        new_total_value_brl = current_state.total_quotas * current_state.quota_price_brl - self.sold_quotas * current_state.quota_price_brl
        new_total_value_usd = current_state.total_quotas * current_state.quota_price_usd - self.sold_quotas * current_state.quota_price_usd
        self.new_total_quotas = current_state.total_quotas - self.sold_quotas
        if self.new_total_quotas > 0:  # avoid division by zero
            self.new_quota_price_brl = new_total_value_brl / self.new_total_quotas
            self.new_quota_price_usd = new_total_value_usd / self.new_total_quotas
        else:
            self.new_quota_price_brl = 0
            self.new_quota_price_usd = 0
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_type = 'redemption'

class AssetValuationEvent(QuotaEvent):
    def apply(self):
        # Calculate the new total portfolio value and adjust the quota price
        portfolio_investments = self.portfolio.portfolioinvestment_set.all()
        new_total_value_brl = sum([inv.total_today_brl for inv in portfolio_investments])
        new_total_value_usd = sum([inv.total_today_usd for inv in portfolio_investments])
        self.new_total_quotas = self.portfolio.quotastate.total_quotas
        self.new_quota_price_brl = new_total_value_brl / self.new_total_quotas
        self.new_quota_price_usd = new_total_value_usd / self.new_total_quotas
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_type = 'asset_valuation'

# Outras classes ainda não muito certo se vale a pena implementar

# class CapitalGainEvent(QuotaEvent):
#     gain_amount_brl = models.FloatField()  # the gain amount in BRL
#     gain_amount_usd = models.FloatField()  # the gain amount in USD
    
#     def apply(self):
#         self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl + self.gain_amount_brl / self.portfolio.quotastate.total_quotas
#         self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd + self.gain_amount_usd / self.portfolio.quotastate.total_quotas


# class CapitalLossEvent(QuotaEvent):
#     loss_amount_brl = models.FloatField()  # the loss amount in BRL
#     loss_amount_usd = models.FloatField()  # the loss amount in USD
    
#     def apply(self):
#         self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl - self.loss_amount_brl / self.portfolio.quotastate.total_quotas
#         self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd - self.loss_amount_usd / self.portfolio.quotastate.total_quotas


# class ExpenseEvent(QuotaEvent):
#     expense_amount_brl = models.FloatField()  # the expense amount in BRL
#     expense_amount_usd = models.FloatField()  # the expense amount in USD
    
#     def apply(self):
#         self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl - self.expense_amount_brl / self.portfolio.quotastate.total_quotas
#         self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd - self.expense_amount_usd / self.portfolio.quotastate.total_quotas

# class InterestEvent(QuotaEvent):
#     interest_amount_brl = models.FloatField()  # the interest amount in BRL
#     interest_amount_usd = models.FloatField()  # the interest amount in USD
    
#     def apply(self):
#         self.new_quota_price_brl = self.portfolio.quotastate.quota_price_brl + self.interest_amount_brl / self.portfolio.quotastate.total_quotas
#         self.new_quota_price_usd = self.portfolio.quotastate.quota_price_usd + self.interest_amount_usd / self.portfolio.quotastate.total_quotas
