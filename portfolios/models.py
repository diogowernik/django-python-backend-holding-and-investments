from datetime import date
from email import message
from hashlib import new
from django import forms
from django.db import models
from django.contrib.auth.models import User
from requests import delete
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
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()
    share_average_price_brl = models.FloatField(default=0)
    dividends_profit = models.FloatField(default=0)
    trade_profit = models.FloatField(default=0)
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

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
        verbose_name_plural = "   Portfolio Assets"


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
    profit = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        try:
            self.portfolio_asset = PortfolioAsset.objects.get(
                portfolio=self.portfolio, asset=self.asset, broker=self.broker)

            if self.order == 'Buy':
                self.share_cost_brl = round(
                    self.share_cost_brl, 2)
                self.total_cost_brl = round(
                    self.shares_amount * self.share_cost_brl, 2)
                self.portfolio_avarage_price = round(
                    ((self.portfolio_asset.share_average_price_brl * self.portfolio_asset.shares_amount) +
                     (self.share_cost_brl * self.shares_amount)) / (self.portfolio_asset.shares_amount + self.shares_amount), 2)
                self.profit = 0

                self.portfolio_asset.broker = self.broker
                self.portfolio_asset.shares_amount += self.shares_amount
                self.portfolio_asset.share_average_price_brl = self.portfolio_avarage_price

            if self.order == 'Sell':
                if self.portfolio_asset.shares_amount < self.shares_amount:
                    raise ValidationError(
                        message='You do not have enough shares to sell.',
                        code='unique_together',
                    )
                last_transaction = Transaction.objects.filter(
                    portfolio=self.portfolio, asset=self.asset).order_by('-id').first()
                self.total_cost_brl = round(
                    self.shares_amount * self.share_cost_brl, 2) * -1
                self.portfolio_avarage_price = round(
                    self.portfolio_asset.share_average_price_brl, 2)
                self.profit = round(
                    (self.total_cost_brl * -1) - (self.portfolio_avarage_price * self.shares_amount), 2)

                # update portfolio asset
                self.portfolio_asset.shares_amount -= self.shares_amount
                self.portfolio_asset.trade_profit += self.profit

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
                self.portfolio_avarage_price = self.share_cost_brl
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

        # Cria PortfolioToken

        if PortfolioToken.objects.filter(portfolio=self.portfolio).exists():
            last = PortfolioToken.objects.filter(
                portfolio=self.portfolio).latest('id')
            PortfolioToken.objects.create(
                portfolio=self.portfolio,
                date=self.date,
                total_today_brl=self.total_cost_brl + last.total_today_brl,
                order_value=self.total_cost_brl
            )
        else:
            PortfolioToken.objects.create(
                portfolio=self.portfolio,
                date=self.date,
                total_today_brl=self.total_cost_brl,
                order_value=self.total_cost_brl
            )

    # def delete undo the transaction
    # def delete(self, *args, **kwargs):
    #     if self.order == 'Buy':
    #         self.portfolio_asset.shares_amount -= self.shares_amount
    #         self.portfolio_asset.trade_profit -= self.profit
    #         self.portfolio_asset.save()
    #         self.portfolio_asset.portfolio.save()
    #     if self.order == 'Sell':
    #         self.portfolio_asset.shares_amount += self.shares_amount
    #         self.portfolio_asset.trade_profit += self.profit
    #         self.portfolio_asset.save()
    #         self.portfolio_asset.portfolio.save()
    #     # delete PortfolioToken
    #     PortfolioToken.objects.filter(
    #         portfolio=self.portfolio).latest('id').delete()

    #     super(Transaction, self).delete(*args, **kwargs)

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
            self.tokens_amount = self.order_value
            self.token_price = self.total_today_brl/self.tokens_amount
            self.profit = (self.total_today_brl -
                           self.order_value)/self.order_value
            self.historical_average_price = 1
            self.historical_profit = self.profit

        super(PortfolioToken, self).save(*args, **kwargs)
