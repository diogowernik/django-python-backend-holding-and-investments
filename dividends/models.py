from django.db import models
from investments.models import Asset
from portfolios.models import PortfolioInvestment
from django.core.exceptions import ValidationError
from cashflow.models import AssetTransaction, AssetAveragePrice

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends")
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)

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
            assets_transactions = AssetAveragePrice.objects.filter(portfolio_investment=portfolio_investment_obj, transaction_date__lte=self.record_date)

            # verifica se existe alguma transação
            if assets_transactions.exists():
                latest_asset_transaction = assets_transactions.latest('transaction_date')

                # por ultimo, crie o PortfolioDividend
                PortfolioDividend.objects.create( 
                    asset=self.asset,
                    category=self.asset.category,
                    record_date=self.record_date,
                    pay_date=self.pay_date,
                    value_per_share_brl=self.value_per_share_brl,
                    value_per_share_usd=self.value_per_share_usd,
                    shares_amount=latest_asset_transaction.total_shares,
                    portfolio_investment=latest_asset_transaction.portfolio_investment,
                    average_price_brl=latest_asset_transaction.share_average_price_brl,
                    average_price_usd=latest_asset_transaction.share_average_price_usd,
                ) 

    
    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos por ativo"

class PortfolioDividend(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
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

    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)

    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)

    def __str__(self):
        return ' {} '.format(self.portfolio.name)

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