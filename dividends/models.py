from django.db import models
from investments.models import Asset
from portfolios.models import PortfolioInvestment
from django.core.exceptions import ValidationError
from cashflow.models import TransactionsHistory
from django.utils import timezone

# Encapsular internamente em funções menores.
class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends", default=1)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Dividend, self).save(*args, **kwargs)  # salvando o Dividendo primeiro
        self.create_portfolio_dividends()

    def get_latest_asset_transaction(self, portfolio_investment_obj):
        historical_average_prices = TransactionsHistory.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date)
        
        if historical_average_prices.exists():
            return historical_average_prices.latest('transaction_date')
        return None

    def create_portfolio_dividends(self):
        portfolio_investments_by_asset = PortfolioInvestment.objects.filter(asset=self.asset).values('broker', 'portfolio').distinct()

        for portfolio_investment in portfolio_investments_by_asset:
            portfolio_investment_obj = PortfolioInvestment.objects.get(broker=portfolio_investment['broker'], portfolio=portfolio_investment['portfolio'], asset=self.asset)

            latest_asset_transaction = self.get_latest_asset_transaction(portfolio_investment_obj)
            
            if latest_asset_transaction is not None:
                self.create_dividends_for_portfolios(latest_asset_transaction)

    def create_dividends_for_portfolios(self, latest_asset_transaction):
        PortfolioDividend.objects.create( 
            asset=self.asset,
            category=self.asset.category,
            record_date=self.record_date,
            pay_date=self.pay_date,
            value_per_share_brl=self.value_per_share_brl,
            value_per_share_usd=self.value_per_share_usd,
            dividend=self,
            shares_amount=latest_asset_transaction.total_shares,
            portfolio_investment=latest_asset_transaction.portfolio_investment,
            average_price_brl=latest_asset_transaction.share_average_price_brl,
            average_price_usd=latest_asset_transaction.share_average_price_usd,
        )
        
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
    dividend = models.ForeignKey(Dividend, on_delete=models.CASCADE, null=True, blank=True)
    categoryChoice = (
        ('Ações Brasileiras', 'Ações Brasileiras'),
        ('Fundos Imobiliários', 'Fundos Imobiliários'),
        ('ETFs', 'ETFs'),
        ('Stocks', 'Stocks'),
        ('REITs', 'REITs'),
        ('Propriedades', 'Propriedades'),
        ('FII', 'Fundos Imobiliários'),
        ('FI-Infra', 'Fundos Imobiliários'),
        ('Ação', 'Ações Brasileiras'),
    )
    category = models.CharField(max_length=100, choices=categoryChoice, default='Ação')
    # category, mudar para asset.category, ou criar um campo dividend_category

    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)

    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)

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