from datetime import date
from django.db import models
from django.contrib.auth.models import User
from investments.models import Asset
from django.core.exceptions import ValidationError
from django.db.models import Q



class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)
    
    class Meta:
        verbose_name_plural = "   Portfolios"

class Broker(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)
    
    class Meta:
        verbose_name_plural = "   Brokers" # Espaços em Branco organizam quem vem primeiro

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    shares_amount = models.FloatField() 
    share_average_price_brl = models.FloatField()
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)    

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        # if self.__class__.objects.filter(portfolio=self.portfolio, asset=self.asset).filter(~Q(id=self.id)).exists():
        if self.__class__.objects.\
                filter(portfolio=self.portfolio, asset=self.asset).\
                exclude(id=self.id).\
                exists():
            raise ValidationError(
                message='This asset already exists in this portfolio.',
                code='unique_together',
            )
    def save(self, *args, **kwargs):
        self.total_cost_brl = round(self.shares_amount * self.share_average_price_brl, 2)
        self.total_today_brl = round(self.shares_amount * self.asset.price, 2)
        super(PortfolioAsset, self).save(*args, **kwargs)

    @property
    def profit(self):
        return  round(self.total_today_brl - self.total_cost_brl, 2)

    @property
    def category(self):
        return self.asset.category

    def __str__(self):
        return ' {} | Qtd = {} | Avg price = {} '.format(self.asset.ticker, self.shares_amount ,self.share_average_price_brl)

    class Meta:
        verbose_name_plural = "  Portfolio Assets"

class BrokerAsset(models.Model):
    portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, default=1)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField() 
    share_average_price_brl = models.FloatField()
    total_cost_brl = models.FloatField(editable=False)
    total_today_brl = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        self.total_cost_brl = round(self.shares_amount * self.share_average_price_brl, 2)
        self.total_today_brl = round(self.shares_amount * self.portfolio_asset.asset.price, 2)
        super(BrokerAsset, self).save(*args, **kwargs)
    
    @property
    def ticker(self):
        return self.portfolio_asset.asset.ticker
    
    def __str__(self):
        return ' {} | {} '.format(self.portfolio_asset.asset.ticker, self.broker)

    class Meta:
        verbose_name_plural = "  Assets per Broker"

class Transaction(models.Model):
    OrderChoices = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )
    date =  models.DateField(("Date"), default=date.today)
    order = models.CharField(max_length = 8, choices = OrderChoices) 
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    shares_amount = models.FloatField()
    share_cost_brl = models.FloatField()
    total_cost_brl = models.FloatField(editable=False)
    portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, editable=False)
    portfolio_avarage_price = models.FloatField(editable=False)
    broker_asset = models.ForeignKey(BrokerAsset, on_delete=models.CASCADE, default=1, editable=False)
    broker_average_price = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        self.share_cost_brl = round(self.share_cost_brl, 2)
        self.total_cost_brl = round(self.shares_amount * self.share_cost_brl, 2)
        # Atualiza PortfolioAsset
        try:
            self.portfolio_asset = PortfolioAsset.objects.get(portfolio=self.portfolio, asset=self.asset)
            self.portfolio_avarage_price = round((self.portfolio_asset.share_average_price_brl * self.portfolio_asset.shares_amount + self.shares_amount * self.share_cost_brl) / (self.portfolio_asset.shares_amount + self.shares_amount), 2)
            if self.order == 'Buy':
                self.portfolio_asset.shares_amount += self.shares_amount
                self.portfolio_asset.share_average_price_brl = self.portfolio_avarage_price
            if self.order == 'Sell':
                self.portfolio_asset.shares_amount -= self.shares_amount
            self.portfolio_asset.save()
        except PortfolioAsset.DoesNotExist:
            self.portfolio_asset = PortfolioAsset.objects.create(portfolio=self.portfolio, asset=self.asset, shares_amount=self.shares_amount, share_average_price_brl=self.share_cost_brl)
            self.portfolio_avarage_price=self.share_cost_brl 
            self.portfolio_asset.save()
        # Atualiza BrokerAsset
        try:
            self.broker_asset = BrokerAsset.objects.get(portfolio_asset=self.portfolio_asset, broker=self.broker)
            self.broker_average_price = round((self.broker_asset.share_average_price_brl * self.broker_asset.shares_amount + self.shares_amount * self.share_cost_brl) / (self.broker_asset.shares_amount + self.shares_amount), 2)
            if self.order == 'Buy':
                self.broker_asset.shares_amount += self.shares_amount
                self.broker_asset.share_average_price_brl = self.broker_average_price
            if self.order == 'Sell':
                self.broker_asset.shares_amount -= self.shares_amount
            self.broker_asset.save()
        except BrokerAsset.DoesNotExist:
            self.broker_asset = BrokerAsset.objects.create(broker=self.broker, portfolio_asset=self.portfolio_asset, shares_amount=self.shares_amount, share_average_price_brl=self.share_cost_brl)
            self.broker_average_price=self.share_cost_brl 
            self.broker_asset.save()


        super(Transaction, self).save(*args, **kwargs) 
        
    def __str__(self):
        return '{}'.format(self.portfolio_asset.asset.ticker)

    class Meta:
        verbose_name_plural = "  Transactions"
    
    # @receiver(pre_save, sender=Transaction)
    # def update_balance_account(sender, instance, update_fields=None, **kwargs):
    #     trans = Transaction.objects.get(portfolio_asset=instance.portfolio_asset, id=instance.id, UserID=instance.UserID)
    #     instance.portfolio_asset.shares_amount -= trans.shares_amount
    #     instance.portfolio_asset.save()

    # Atualiza valores no Portfolio Assets na atualização de ordens estudar depois

    # def delete(self, *args, **kwargs):
    #     self.portfolio_asset.shares_amount -= self.shares_amount
    #     self.portfolio_asset.save()
    #     super(Transaction, self).delete(*args, **kwargs) 







    