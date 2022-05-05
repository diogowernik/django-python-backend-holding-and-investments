from datetime import date
from hashlib import new
from django.db import models
from django.contrib.auth.models import User
from investments.models import Asset
from brokers.models import Broker
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = "     Portfolios"


class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    shares_amount = models.FloatField()
    share_average_price_brl = models.FloatField(default=0)
    dividends_profit = models.FloatField(default=0)
    trade_profit = models.FloatField(default=0)
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self.__class__.objects.\
                filter(portfolio=self.portfolio, asset=self.asset).\
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
        verbose_name_plural = "   Portfolio Assets"


class BrokerAsset(models.Model):
    portfolio_asset = models.ForeignKey(
        PortfolioAsset, on_delete=models.CASCADE, default=1)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()
    share_average_price_brl = models.FloatField()
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        self.total_cost_brl = round(
            self.shares_amount * self.share_average_price_brl, 2)
        self.total_today_brl = round(
            self.shares_amount * self.portfolio_asset.asset.price, 2)
        super(BrokerAsset, self).save(*args, **kwargs)

    @property
    def ticker(self):
        return self.portfolio_asset.asset.ticker

    def __str__(self):
        return ' {} | {} '.format(self.portfolio_asset.asset.ticker, self.broker)

    class Meta:
        verbose_name_plural = "  Portfolio Assets (per Broker)"


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
    portfolio_avarage_price = models.FloatField(editable=False)
    broker_asset = models.ForeignKey(
        BrokerAsset, on_delete=models.CASCADE, default=1, editable=False)
    broker_average_price = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        self.share_cost_brl = round(self.share_cost_brl, 2)
        self.total_cost_brl = round(
            self.shares_amount * self.share_cost_brl, 2)
        # Atualiza PortfolioAsset
        try:
            self.portfolio_asset = PortfolioAsset.objects.get(
                portfolio=self.portfolio, asset=self.asset)
            self.portfolio_avarage_price = round((self.portfolio_asset.share_average_price_brl * self.portfolio_asset.shares_amount +
                                                 self.shares_amount * self.share_cost_brl) / (self.portfolio_asset.shares_amount + self.shares_amount), 2)

            if self.order == 'Buy':
                self.portfolio_asset.shares_amount += self.shares_amount
                self.portfolio_asset.share_average_price_brl = self.portfolio_avarage_price
            if self.order == 'Sell':
                self.portfolio_asset.shares_amount -= self.shares_amount
            self.portfolio_asset.save()
        except PortfolioAsset.DoesNotExist:
            self.portfolio_asset = PortfolioAsset.objects.create(
                portfolio=self.portfolio, asset=self.asset, shares_amount=self.shares_amount, share_average_price_brl=self.share_cost_brl)
            self.portfolio_avarage_price = self.share_cost_brl
            self.portfolio_asset.save()
        # Atualiza BrokerAsset
        try:
            self.broker_asset = BrokerAsset.objects.get(
                portfolio_asset=self.portfolio_asset, broker=self.broker)
            self.broker_average_price = round((self.broker_asset.share_average_price_brl * self.broker_asset.shares_amount +
                                              self.shares_amount * self.share_cost_brl) / (self.broker_asset.shares_amount + self.shares_amount), 2)
            if self.order == 'Buy':
                self.broker_asset.shares_amount += self.shares_amount
                self.broker_asset.share_average_price_brl = self.broker_average_price
            if self.order == 'Sell':
                self.broker_asset.shares_amount -= self.shares_amount
            self.broker_asset.save()
        except BrokerAsset.DoesNotExist:
            self.broker_asset = BrokerAsset.objects.create(
                broker=self.broker, portfolio_asset=self.portfolio_asset, shares_amount=self.shares_amount, share_average_price_brl=self.share_cost_brl)
            self.broker_average_price = self.share_cost_brl
            self.broker_asset.save()

        super(Transaction, self).save(*args, **kwargs)
        # Cria PortfolioToken

        if PortfolioToken.objects.exists():
            last = PortfolioToken.objects.latest('id')
            if self.order == 'Buy':
                PortfolioToken.objects.create(
                    # transaction_id=self.id,
                    portfolio=self.portfolio,
                    date=self.date,
                    total_today_brl=self.total_cost_brl + last.total_today_brl,
                    order_value=self.total_cost_brl
                )
            if self.order == 'Sell':
                PortfolioToken.objects.create(
                    # transaction_id=self.id,
                    portfolio=self.portfolio,
                    date=self.date,
                    total_today_brl=last.total_today_brl - self.total_cost_brl,
                    order_value=- self.total_cost_brl
                )
        else:
            PortfolioToken.objects.create(
                # transaction_id=self.id,
                portfolio=self.portfolio,
                date=self.date,
                total_today_brl=self.total_cost_brl,
                order_value=self.total_cost_brl
            )

    def __str__(self):
        return '{}'.format(self.portfolio_asset.asset.ticker)

    class Meta:
        verbose_name_plural = "    Portfolio Transactions"


class PortfolioToken(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, default=1)
    total_today_brl = models.FloatField()
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
        verbose_name_plural = " Porftolio Tokens"

    def save(self, *args, **kwargs):

        if PortfolioToken.objects.exists():
            last = PortfolioToken.objects.latest('id')
            self.tokens_amount = round(
                last.tokens_amount+(self.order_value/last.token_price), 2)
            if self.tokens_amount > 0:
                self.token_price = round(
                    self.total_today_brl/self.tokens_amount, 4)
                self.historical_average_price = (last.tokens_amount*last.historical_average_price+(
                    self.tokens_amount-last.tokens_amount)*last.token_price)/self.tokens_amount
                self.historical_profit = round(
                    (self.token_price-self.historical_average_price)/self.historical_average_price, 4)
            else:
                self.token_price = 1
                self.historical_average_price = 1
                self.historical_profit = 0
            self.profit = round(
                (self.token_price-last.token_price)/last.token_price, 4)

        else:
            self.tokens_amount = self.order_value
            self.token_price = self.total_today_brl/self.tokens_amount
            self.profit = (self.total_today_brl -
                           self.order_value)/self.order_value
            self.historical_average_price = 1
            self.historical_profit = self.profit

        super(PortfolioToken, self).save(*args, **kwargs)
