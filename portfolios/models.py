from datetime import date
from email.policy import default
from unicodedata import category
from django import forms
from django.db import models
from django.contrib.auth.models import User
from requests import delete
from investments.models import Asset
from brokers.models import Broker
from dividends.models import Dividend
from django.core.exceptions import ValidationError
# from django.db.models import Sum


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = " Portfolios"


class PortfolioInvestment(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()

    dividends_profit_brl = models.FloatField(default=0, editable=False)
    dividends_profit_usd = models.FloatField(default=0, editable=False)

    trade_profit_brl = models.FloatField(default=0, editable=False)
    trade_profit_usd = models.FloatField(default=0, editable=False)

    share_average_price_brl = models.FloatField(default=0)
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

    share_average_price_usd = models.FloatField(default=0)
    total_cost_usd = models.FloatField(default=0, editable=False)
    total_today_usd = models.FloatField(default=0, editable=False)

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self.__class__.objects.\
                filter(portfolio=self.portfolio, asset=self.asset, broker=self.broker).\
                exclude(id=self.id).\
                exists():
            raise ValidationError(
                message='This asset already exists in this portfolio.',
                code='unique_together',
            )

    def save(self, *args, **kwargs):
        self.total_cost_brl = round(
            self.shares_amount * self.share_average_price_brl, 2)
        self.total_today_brl = round(
            self.shares_amount * self.asset.price_brl, 2)

        self.total_cost_usd = round(
            self.shares_amount * self.share_average_price_usd, 2)
        self.total_today_usd = round(
            self.shares_amount * self.asset.price_usd, 2)

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
        return ' {} | Qtd = {} | Avg price = {} '.format(self.asset.ticker, self.shares_amount, self.share_average_price_brl)

    class Meta:
        verbose_name_plural = "  Investimentos por Portfolio"


class PortfolioTrade(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.CharField(max_length=15, default='')
    CategoryChoices = (
        ('Criptomoeda', 'Criptomoeda'),
        ('Ação', 'Ação'),
        ('FII', 'FII'),
        ('Stock', 'Stock'),
        ('REIT', 'REIT'),
        ('ETF', 'ETF'),
        ('Currency', 'Currency'),
    )
    category = models.CharField(
        max_length=15, choices=CategoryChoices, default='Ação')
    OrderChoices = (
        ('C', 'Compra'),
        ('V', 'Venda'),
    )
    order = models.CharField(max_length=8, choices=OrderChoices, default='C')
    date = models.DateField(("Date"), default=date.today)

    shares_amount = models.FloatField(default=0)

    share_cost_brl = models.FloatField(default=0)
    share_cost_usd = models.FloatField(default=0)

    total_cost_brl = models.FloatField(editable=False, default=0)
    total_cost_usd = models.FloatField(editable=False, default=0)

    tax_brl = models.FloatField(default=0, editable=False)
    tax_usd = models.FloatField(default=0, editable=False)

    usd_on_date = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.total_cost_brl = round(
            self.shares_amount * self.share_cost_brl, 2)
        self.total_cost_usd = round(
            self.shares_amount * self.share_cost_usd, 2)
        self.usd_on_date = round(
            self.share_cost_brl / self.share_cost_usd, 2)
        self.tax_brl = round(
            (self.total_cost_brl * self.broker.tax_percent) + self.broker.tax_brl, 2)
        self.tax_usd = round(
            (self.total_cost_usd * self.broker.tax_percent) + self.broker.tax_usd, 2)

        super(PortfolioTrade, self).save(*args, **kwargs)
        # then create a PortfolioHistory object
        PortfolioHistory.objects.create(
            portfolio=self.portfolio,
            trade=self,
            asset=self.asset)

    def __str__(self):
        return '{}'.format(self.asset)

    class Meta:
        verbose_name_plural = " Transações por Portfolio"


class PortfolioDividend(models.Model):
    # portfolio_asset = models.ForeignKey(
    #     PortfolioInvestment, on_delete=models.CASCADE, default=1)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=2)

    ticker = models.CharField(max_length=10, default='0')
    categoryChoice = (
        ('Ações Brasileiras', 'Ações Brasileiras'),
        ('Fundos Imobiliários', 'Fundos Imobiliários'),
        ('ETFs', 'ETFs'),
        ('Stocks', 'Stocks'),
        ('REITs', 'REITs'),
        ('Propriedades', 'Propriedades'),
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


class PortfolioHistory(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=2)
    trade = models.ForeignKey(
        PortfolioTrade, on_delete=models.CASCADE, default=1)
    asset = models.CharField(max_length=15, default='HGLG11')
    broker = models.ForeignKey(
        Broker, on_delete=models.CASCADE, default=1)

    total_shares = models.FloatField(default=0, editable=False)

    share_average_price_brl = models.FloatField(default=0, editable=False)
    share_average_price_usd = models.FloatField(default=0, editable=False)

    trade_profit_brl = models.FloatField(default=0, editable=False)
    trade_profit_usd = models.FloatField(default=0, editable=False)

    def __str__(self):
        return ' {} '.format(self.portfolio.name)

    class Meta:
        verbose_name_plural = "Evolução do Portfolio"

    @property
    def order(self):
        return self.trade.order

    @property
    def date(self):
        return self.trade.date

    @property
    def shares_amount(self):
        return self.trade.shares_amount

    @property
    def share_cost_brl(self):
        return self.trade.share_cost_brl

    @property
    def total_cost_brl(self):
        return self.trade.total_cost_brl

    @property
    def total_on_date_brl(self):
        return round(self.total_shares * self.share_average_price_brl, 2)

    @property
    def total_on_date_usd(self):
        return round(self.total_shares * self.share_average_price_usd, 2)

    @property
    def tax_brl(self):
        return self.trade.tax_brl

    @property
    def share_cost_usd(self):
        return self.trade.share_cost_usd

    @property
    def total_cost_usd(self):
        return self.trade.total_cost_usd

    @property
    def tax_usd(self):
        return self.trade.tax_usd

    def save(self, *args, **kwargs):
        self.broker = self.trade.broker
        # if order == 'C':
        if self.order == 'C':
            if PortfolioHistory.objects.filter(portfolio=self.portfolio, asset=self.trade.asset).exists():
                last_portfolio_history = PortfolioHistory.objects.filter(
                    portfolio=self.portfolio, asset=self.asset).last()
                self.total_shares = last_portfolio_history.total_shares + self.trade.shares_amount
                self.share_average_price_brl = round(
                    (last_portfolio_history.total_shares * last_portfolio_history.share_average_price_brl + (self.trade.total_cost_brl + self.trade.tax_brl)) / self.total_shares, 2)
                self.share_average_price_usd = round(
                    (last_portfolio_history.total_shares * last_portfolio_history.share_average_price_usd + (self.trade.total_cost_usd + self.trade.tax_usd)) / self.total_shares, 2)
                self.trade_profit_brl = 0
                self.trade_profit_usd = 0
            else:
                self.total_shares = self.trade.shares_amount
                self.share_average_price_brl = round(
                    (self.trade.total_cost_brl + self.trade.tax_brl) / self.trade.shares_amount, 2)
                self.share_average_price_usd = round(
                    (self.trade.total_cost_usd + self.trade.tax_usd) / self.trade.shares_amount, 2)
                self.trade_profit_brl = 0
                self.trade_profit_usd = 0

        # elif order == 'V':
        else:
            last_portfolio_history = PortfolioHistory.objects.filter(
                portfolio=self.portfolio, asset=self.asset, broker=self.trade.broker).last()
            self.total_shares = last_portfolio_history.total_shares - self.trade.shares_amount

            self.share_average_price_brl = last_portfolio_history.share_average_price_brl
            self.share_average_price_usd = last_portfolio_history.share_average_price_usd
            self.trade_profit_brl = round(
                self.trade.total_cost_brl - ((self.trade.shares_amount * self.share_average_price_brl) + self.trade.tax_brl), 2)
            self.trade_profit_usd = round(
                self.trade.total_cost_usd - ((self.trade.shares_amount * self.share_average_price_usd) + self.trade.tax_usd), 2)

        super(PortfolioHistory, self).save(*args, **kwargs)

        # if self.trade.order == C
        # than create or Update PortfolioInvestement
        # falta criar uma logica para o USD e BRL diferente da para outros ativos. Considerando que USD e BRL são caixa do portfolio
        if self.trade.order == 'C':
            if PortfolioInvestment.objects.filter(portfolio=self.portfolio, broker=self.trade.broker, asset=Asset.objects.get(ticker=self.asset)).exists():
                portfolio_investment = PortfolioInvestment.objects.get(
                    portfolio=self.portfolio, asset=Asset.objects.get(ticker=self.asset), broker=self.trade.broker)
                portfolio_investment.share_average_price_brl = self.share_average_price_brl
                portfolio_investment.share_average_price_usd = self.share_average_price_usd
                if portfolio_investment.asset == Asset.objects.get(ticker='USD'):
                    portfolio_investment.shares_amount = portfolio_investment.shares_amount + \
                        self.trade.total_cost_usd
                elif portfolio_investment.asset == Asset.objects.get(ticker='BRL'):
                    portfolio_investment.shares_amount = portfolio_investment.shares_amount + \
                        self.trade.total_cost_brl
                else:
                    portfolio_investment.shares_amount = self.total_shares

                portfolio_investment.save()
            else:
                PortfolioInvestment.objects.create(
                    portfolio=self.portfolio,
                    asset=Asset.objects.get(ticker=self.asset),
                    broker=self.trade.broker,
                    shares_amount=self.total_shares,
                    share_average_price_brl=self.share_average_price_brl,
                    share_average_price_usd=self.share_average_price_usd
                )
            # Update Portfolio Balance if asset is not USD will update USD balance
            current_asset = Asset.objects.get(ticker=self.asset)
            if current_asset.ticker != 'USD':
                portfolio_balance = PortfolioInvestment.objects.get(
                    portfolio=self.portfolio, broker=self.trade.broker, asset=Asset.objects.get(ticker='USD'))
                portfolio_balance.shares_amount = portfolio_balance.shares_amount - \
                    self.trade.total_cost_usd
                portfolio_balance.save()
            elif current_asset.ticker != 'BRL':
                portfolio_balance = PortfolioInvestment.objects.get(
                    portfolio=self.portfolio, broker=self.trade.broker, asset=Asset.objects.get(ticker='BRL'))
                portfolio_balance.shares_amount = portfolio_balance.shares_amount - \
                    self.trade.total_cost_brl
                portfolio_balance.save()
            else:
                pass  # pass because the asset is USD or BRL

        # elif self.trade.order == V
        else:
            portfolio_investment = PortfolioInvestment.objects.get(
                portfolio=self.portfolio, broker=self.trade.broker, asset=Asset.objects.get(ticker=self.asset))
            portfolio_investment.shares_amount = self.total_shares
            portfolio_investment.broker = self.trade.broker
            portfolio_investment.share_average_price_brl = self.share_average_price_brl
            portfolio_investment.share_average_price_usd = self.share_average_price_usd
            portfolio_investment.trade_profit_brl = self.trade_profit_brl
            portfolio_investment.save()

            # Update Portfolio Balance if asset is not USD will update USD balance
            current_asset = Asset.objects.get(ticker=self.asset)
            if current_asset.ticker != 'USD':
                portfolio_balance = PortfolioInvestment.objects.get(
                    portfolio=self.portfolio, broker=self.trade.broker, asset=Asset.objects.get(ticker='USD'))
                portfolio_balance.shares_amount = portfolio_balance.shares_amount + \
                    self.trade.total_cost_usd
                portfolio_balance.save()
