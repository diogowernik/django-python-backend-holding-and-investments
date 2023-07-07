from django.db import models
from investments.models import Asset
from portfolios.models import PortfolioInvestment
from django.core.exceptions import ValidationError
from cashflow.models import AssetTransaction, AssetAveragePrice, TransactionsHistory
from django.utils import timezone

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends", default=1)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Dividend, self).save(*args, **kwargs)  # salvando o Dividendo primeiro
        self.create_portfolio_dividends()

    def create_portfolio_dividends(self):
        # Primeiro, obtenha todas as combinações únicas de broker, asset e portfolio
        portfolio_investments_by_asset = PortfolioInvestment.objects.filter(asset=self.asset).values('broker', 'portfolio').distinct()

        # Agora, para cada combinação broker, asset e portfolio, crie um PortfolioDividend encontra as assets_transactions pela record_date
        for portfolio_investment in portfolio_investments_by_asset:
            portfolio_investment_obj = PortfolioInvestment.objects.get(broker=portfolio_investment['broker'], portfolio=portfolio_investment['portfolio'], asset=self.asset)

            # filtre as transações do ativo pela data de registro (record_date)
            historical_average_prices = TransactionsHistory.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date)

            # verifica se existe alguma transação
            if historical_average_prices.exists():
                latest_asset_transaction = historical_average_prices.latest('transaction_date')

                # por ultimo, crie o PortfolioDividend
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

    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)

    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Dividendos por Portfolio"

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