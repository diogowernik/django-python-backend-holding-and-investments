from datetime import date
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


class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()
    dividends_profit = models.FloatField(default=0)
    trade_profit = models.FloatField(default=0)

    share_average_price_brl = models.FloatField(default=0)
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

    share_average_price_usd = models.FloatField(default=0)
    total_cost_usd = models.FloatField(default=0)
    total_today_usd = models.FloatField(default=0)

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
        self.total_today_brl = round(self.shares_amount * self.asset.price, 2)
        super(PortfolioAsset, self).save(*args, **kwargs)

    @property
    def ticker(self):
        return self.asset.ticker

    @property
    def profit(self):
        return round(self.total_today_brl - self.total_cost_brl + self.dividends_profit + self.trade_profit, 2)

    @property
    def category(self):
        return self.asset.category

    def __str__(self):
        return ' {} | Qtd = {} | Avg price = {} '.format(self.asset.ticker, self.shares_amount, self.share_average_price_brl)

    class Meta:
        verbose_name_plural = "  Investimentos por Portfolio"


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    OrderChoices = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )
    date = models.DateField(("Date"), default=date.today)
    order = models.CharField(max_length=8, choices=OrderChoices)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()
    share_cost_brl = models.FloatField()

    total_cost_brl = models.FloatField(editable=False)
    portfolio_asset = models.ForeignKey(
        PortfolioAsset, on_delete=models.CASCADE, editable=False)

    def save(self, *args, **kwargs):
        try:
            # Get the portfolio asset
            self.portfolio_asset = PortfolioAsset.objects.get(
                portfolio=self.portfolio, asset=self.asset, broker=self.broker)

            if self.order == 'Buy':
                self.share_cost_brl = round(
                    self.share_cost_brl, 2)
                self.total_cost_brl = round(
                    self.shares_amount * self.share_cost_brl, 2)

                self.portfolio_asset.broker = self.broker
                self.portfolio_asset.shares_amount += self.shares_amount
                # need to update the average price from asset in portfolio asset
                # create a worker for that

            if self.order == 'Sell':
                if self.portfolio_asset.shares_amount < self.shares_amount:
                    raise ValidationError(
                        message='You do not have enough shares to sell.',
                        code='unique_together',
                    )
                self.total_cost_brl = round(
                    self.shares_amount * self.share_cost_brl, 2) * -1

                # update portfolio asset
                self.portfolio_asset.shares_amount -= self.shares_amount

            self.portfolio_asset.save()
            self.portfolio_asset.portfolio.save()

        except PortfolioAsset.DoesNotExist:
            if self.order == 'Buy':
                self.portfolio_asset = PortfolioAsset.objects.create(
                    portfolio=self.portfolio,
                    asset=self.asset,
                    broker=self.broker,
                    shares_amount=self.shares_amount,
                    share_average_price_brl=self.share_cost_brl
                )
                self.total_cost_brl = round(
                    self.shares_amount * self.share_cost_brl, 2)
                self.portfolio_asset.save()
            if self.order == 'Sell':
                # not save transaction because it's not a valid transaction
                raise forms.ValidationError(
                    message='This asset does not exist in this portfolio.',
                    code='unique_together',
                )

            self.portfolio_asset.save()
            self.portfolio_asset.portfolio.save()
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.portfolio_asset.asset.ticker)

    class Meta:
        verbose_name_plural = " Transações"


class PortfolioToken(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    total_today_brl = models.FloatField()
    total_today_usd = models.FloatField(default=0)
    order_value = models.FloatField()
    date = models.DateField(("Date"), default=date.today)
    tokens_amount = models.FloatField(editable=False)
    token_price = models.FloatField(editable=False)
    profit = models.FloatField(editable=False, default=1)
    historical_average_price = models.FloatField(editable=False, default=1)
    historical_profit = models.FloatField(editable=False)

    def __str__(self):
        return ' {} '.format(self.portfolio.name)

    class Meta:
        verbose_name_plural = "Evolução do Portfolio"

    def save(self, *args, **kwargs):
        # save object filtered by portfolio
        if PortfolioToken.objects.filter(portfolio=self.portfolio).exists():
            last = PortfolioToken.objects.filter(
                portfolio=self.portfolio).latest('id')
            self.tokens_amount = round(
                last.tokens_amount+(self.order_value/last.token_price), 2)
            if self.tokens_amount > 0:
                self.token_price = round(
                    self.total_today_brl/self.tokens_amount, 4)
                # remove historical average price
                self.historical_average_price = (last.tokens_amount*last.historical_average_price+(
                    self.tokens_amount-last.tokens_amount)*last.token_price)/self.tokens_amount
                # historical profit = (self.token_price/1 -1) *100
                self.historical_profit = round(
                    (self.token_price/1 - 1), 4)
            else:
                self.token_price = 1
                self.historical_average_price = 1
                self.historical_profit = 0
            self.profit = round(
                (self.token_price-last.token_price)/last.token_price, 4)

        else:
            self.tokens_amount = self.total_today_brl
            self.token_price = 1
            # self.token_price = self.total_today_brl/self.tokens_amount
            self.profit = 0
            self.historical_average_price = 1
            self.historical_profit = self.profit

        super(PortfolioToken, self).save(*args, **kwargs)


class PortfolioDividend(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    dividend = models.ForeignKey(
        Dividend, on_delete=models.CASCADE, default=1)
    portfolio_asset = models.ForeignKey(
        PortfolioAsset, on_delete=models.CASCADE, default=1)

    @property
    def total_dividend_brl(self):
        return round(self.dividend.value_per_share_brl * self.portfolio_asset.shares_amount, 2)

    @property
    def average_price_brl(self):
        return round(self.portfolio_asset.share_average_price_brl, 2)

    @property
    def yield_on_cost(self):
        return round(self.dividend.value_per_share_brl/self.average_price_brl, 4) * 100

    def __str__(self):
        return ' {} '.format(self.portfolio.name)

    class Meta:
        verbose_name_plural = "Dividendos por Portfolio"
