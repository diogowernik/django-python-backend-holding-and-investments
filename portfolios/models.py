
from django.db import models
from django.contrib.auth.models import User
from investments.models import Asset
from brokers.models import Broker
from categories.models import Category
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = " Portfolios"

class PortfolioInvestment(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=22)
    shares_amount = models.FloatField(default=0)

    dividends_profit_brl = models.FloatField(default=0, editable=False)
    dividends_profit_usd = models.FloatField(default=0, editable=False)
    trade_profit_brl = models.FloatField(default=0, editable=False)
    trade_profit_usd = models.FloatField(default=0, editable=False)

    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)
    total_cost_brl = models.FloatField(editable=False, default=0)
    total_cost_usd = models.FloatField(default=0, editable=False)

    total_today_brl = models.FloatField(editable=False, default=0)
    total_today_usd = models.FloatField(default=0, editable=False)

    def save(self, *args, **kwargs):
        self.total_cost_brl = round(self.shares_amount * self.share_average_price_brl, 2)
        self.total_cost_usd = round(self.shares_amount * self.share_average_price_usd, 2)

        self.total_today_brl = round(self.shares_amount * self.asset.price_brl, 2)
        self.total_today_usd = round(self.shares_amount * self.asset.price_usd, 2)
        super(PortfolioInvestment, self).save(*args, **kwargs)

    @property
    def ticker(self):
        return self.asset.ticker

    @property
    def total_profit_brl(self):
        return round((self.total_today_brl + self.dividends_profit_brl + self.trade_profit_brl) - self.total_cost_brl, 2)

    @property
    def total_profit_usd(self):
        return round((self.total_today_usd + self.dividends_profit_usd + self.trade_profit_usd) - self.total_cost_usd, 2)

    @property
    def category(self):
        return self.asset.category

    @property
    def av_price_minus_div_brl(self):
        return round(self.share_average_price_brl - (self.dividends_profit_brl/self.shares_amount if self.shares_amount > 0 else 0), 2)

    @property
    def av_price_minus_div_usd(self):
        return round(self.share_average_price_usd - (self.dividends_profit_usd/self.shares_amount if self.shares_amount > 0 else 0), 2)

    @property
    def portfolio_percentage(self):
        total_portfolio = PortfolioInvestment.objects.filter(
            portfolio=self.portfolio).aggregate(models.Sum('total_today_brl'))
        return round((self.total_today_brl / total_portfolio['total_today_brl__sum']), 4)

    @property
    def yield_on_cost_brl(self):
        return round((self.dividends_profit_brl / self.total_cost_brl) if self.total_cost_brl > 0 else 0, 4)

    @property
    def yield_on_cost_usd(self):
        return round((self.dividends_profit_usd / self.total_cost_usd) if self.total_cost_usd > 0 else 0, 4)

    @property
    def profit_without_div_trade_brl(self):
        return round((self.total_today_brl - self.total_cost_brl)/self.total_cost_brl if self.total_cost_brl > 0 else 0, 4)

    @property
    def profit_without_div_trade_usd(self):
        return round((self.total_today_usd - self.total_cost_usd)/self.total_cost_usd if self.total_cost_usd > 0 else 0, 4)

    @property
    def profit_with_div_trade_brl(self):
        return round((self.total_profit_brl / self.total_cost_brl) if self.total_cost_brl > 0 else 0, 4)

    @property
    def profit_with_div_trade_usd(self):
        return round((self.total_profit_usd / self.total_cost_usd) if self.total_cost_usd > 0 else 0, 4)

    def __str__(self):
        return ' {} | {} | {} '.format(self.asset.ticker, self.shares_amount, self.asset.ticker)

    class Meta:
        verbose_name_plural = "  Investimentos por Portfolio"
        unique_together = ['portfolio', 'asset', 'broker']

class PortfolioEvolution(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=7)
    category_total_brl = models.FloatField(default=0)
    category_total_usd = models.FloatField(default=0)
    class Meta:
        ordering = ['date']
        verbose_name = 'Evolução do Patrimonio'
        verbose_name_plural = 'Evolução do Patrimonio'

class PortfolioDividend(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=2)

    ticker = models.CharField(max_length=10, default='0')
    categoryChoice = (
        ('Ações Brasileiras', 'Ações Brasileiras'),
        ('Fundos Imobiliários', 'Fundos Imobiliários'),
        ('ETF', 'ETF'),
        ('Stocks', 'Stocks'),
        ('REITs', 'REITs'),
        ('Propriedades', 'Propriedades'),
        ('FII', 'Fundos Imobiliários'),
        ('FI-Infra', 'Fundos Imobiliários'),
        ('Ação', 'Ações Brasileiras'),
    )
    category = models.CharField(
        max_length=100, choices=categoryChoice, default='Ação')
    subcategoryChoice = (
        ('R', 'Rendimentos'),
        ('J', 'JCP'),
        ('D', 'Dividendos'),
        ('A', 'Aluguel'),
    )
    subcategory = models.CharField(
        max_length=10, choices=subcategoryChoice, default='R')

    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)

    value_per_share_brl = models.FloatField(default=0)
    total_dividend_brl = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    dividend_tax = models.FloatField(default=0)

    usd_on_pay_date = models.FloatField(default=0)

    value_per_share_usd = models.FloatField(default=0)
    total_dividend_usd = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)

    yield_on_cost = models.FloatField(default=0)

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