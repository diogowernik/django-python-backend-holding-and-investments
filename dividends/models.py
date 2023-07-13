from django.db import models
from investments.models import Asset
from portfolios.models import PortfolioInvestment
from trade.models import TradeHistory
from categories.models import Category
from django.db.models import Max

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends", default=1)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Dividend, self).save(*args, **kwargs)  # salvando o Dividendo primeiro
        if is_new:
            self.create_portfolio_dividends()
        else:
            self.update_portfolio_dividends()
    
    def update_portfolio_dividends(self):
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=self)
        for portfolio_dividend in portfolio_dividends:
            portfolio_dividend.value_per_share_brl = self.value_per_share_brl
            portfolio_dividend.value_per_share_usd = self.value_per_share_usd
            portfolio_dividend.save()

    def create_portfolio_dividends(self):
        portfolio_investment_objs = self.get_portfolio_investments()
        latest_transactions_dict = self.get_latest_transactions(portfolio_investment_objs)

        for portfolio_investment_obj in portfolio_investment_objs:
            last_transaction_date = latest_transactions_dict.get(portfolio_investment_obj.id)
            if last_transaction_date is not None:
                latest_asset_transaction = TradeHistory.objects.filter(
                    portfolio_investment=portfolio_investment_obj,
                    transaction_date=last_transaction_date
                ).first()
                self.create_dividends_for_portfolios(latest_asset_transaction)

    def get_portfolio_investments(self):
        portfolio_investments_by_asset = PortfolioInvestment.objects.filter(
            asset=self.asset
        ).values('broker', 'portfolio').distinct()

        return PortfolioInvestment.objects.filter(
            broker__in=[x['broker'] for x in portfolio_investments_by_asset],
            portfolio__in=[x['portfolio'] for x in portfolio_investments_by_asset],
            asset=self.asset
        )

    def get_latest_transactions(self, portfolio_investment_objs):
        latest_transactions = TradeHistory.objects.filter(
            portfolio_investment__in=portfolio_investment_objs,
            transaction_date__lte=self.record_date
        ).values('portfolio_investment').annotate(
            last_transaction_date=Max('transaction_date')
        )
        return {x['portfolio_investment']: x['last_transaction_date'] for x in latest_transactions}
    
    def get_latest_asset_transaction(self, portfolio_investment_obj):
        historical_average_prices = TradeHistory.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date)
        
        if historical_average_prices.exists():
            return historical_average_prices.latest('transaction_date')
        return None

    def create_dividends_for_portfolios(self, latest_asset_transaction):
        if latest_asset_transaction.total_shares > 0:
            # Crie PortfolioDividend através da função centralizada
            PortfolioDividend.create_portfolio_dividend(latest_asset_transaction, self)  # foi alterado aqui
        
    def delete(self, *args, **kwargs):
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=self)
        portfolio_dividends.delete()
        super(Dividend, self).delete(*args, **kwargs)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos"

class PortfolioDividend(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    trade_history = models.ForeignKey(TradeHistory, on_delete=models.CASCADE, null=True, blank=True)
    dividend = models.ForeignKey(Dividend, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)

    @classmethod
    def create_portfolio_dividend(cls, trade_history, dividend):
        cls.objects.create(
            portfolio_investment=trade_history.portfolio_investment,
            asset=dividend.asset,
            trade_history=trade_history,
            category=dividend.asset.category,
            record_date=dividend.record_date,
            pay_date=dividend.pay_date,
            value_per_share_brl=dividend.value_per_share_brl,
            value_per_share_usd=dividend.value_per_share_usd,
            dividend=dividend,
            shares_amount=trade_history.total_shares, 
            average_price_brl=trade_history.share_average_price_brl,
            average_price_usd=trade_history.share_average_price_usd,
        )

    @property
    def pay_date_by_month_year(self):
        return self.pay_date.strftime('%m/%Y')

    @property
    def pay_date_by_year(self):
        return self.pay_date.strftime('%Y')

    @property
    def yield_on_cost_brl(self):
        if self.average_price_brl > 0:
            return round((self.value_per_share_brl / self.average_price_brl), 4)

    @property
    def yield_on_cost_usd(self):
        if self.average_price_usd > 0:
            return round((self.value_per_share_usd / self.average_price_usd), 4)
        
    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)
    
    class Meta:
        verbose_name_plural = "Dividendos por Portfolio"

