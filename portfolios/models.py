from datetime import date
from django.db import models
from django.contrib.auth.models import User
from investments.models import Asset

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
    shares_amount = models.DecimalField(max_digits=18, decimal_places=0) 
    share_average_price_brl = models.DecimalField(max_digits=18, decimal_places=2)
    total_cost_brl = models.DecimalField(max_digits=18, decimal_places=2, editable=False)
    total_today_brl = models.DecimalField(max_digits=18, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_cost_brl = self.shares_amount * self.share_average_price_brl
        self.total_today_brl = self.shares_amount * self.asset.price
        super(PortfolioAsset, self).save(*args, **kwargs)

    @property
    def profit(self):
        return  self.total_today_brl - self.total_cost_brl

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
    shares_amount = models.DecimalField(max_digits=18, decimal_places=0) 
    share_average_price_brl = models.DecimalField(max_digits=18, decimal_places=2)
    total_cost_brl = models.DecimalField(max_digits=18, decimal_places=2, editable=False)
    total_today_brl = models.DecimalField(max_digits=18, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_cost_brl = self.shares_amount * self.share_average_price_brl
        self.total_today_brl = self.shares_amount * self.portfolio_asset.asset.price
        super(BrokerAsset, self).save(*args, **kwargs)
    
    @property
    def ticker(self):
        return self.portfolio_asset.asset.ticker
    
    def __str__(self):
        return ' {} | {} '.format(self.portfolio_asset.asset.ticker, self.broker)

    class Meta:
        verbose_name_plural = "  Portfolio Assets"

class Transaction(models.Model):
    OrderChoices = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )
    date =  models.DateField(("Date"), default=date.today)
    portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, default=1)
    broker_asset = models.ForeignKey(BrokerAsset, on_delete=models.CASCADE, default=1)
    shares_amount = models.DecimalField(max_digits=18, decimal_places=0)
    new_average_price = models.DecimalField(max_digits=18, decimal_places=2, editable=False)
    broker_average_price = models.DecimalField(max_digits=18, decimal_places=2, editable=False)
    share_cost_brl = models.DecimalField(max_digits=18, decimal_places=2)
    total_cost_brl = models.DecimalField(max_digits=18, decimal_places=2, editable=False)
    order = models.CharField(max_length = 8, choices = OrderChoices)

    # Atualiza valores no PortfolioAsset
    def save(self, *args, **kwargs):
        self.total_cost_brl = self.shares_amount * self.share_cost_brl
        self.new_average_price = (self.portfolio_asset.share_average_price_brl * self.portfolio_asset.shares_amount + self.shares_amount * self.share_cost_brl) / (self.portfolio_asset.shares_amount + self.shares_amount)
        self.broker_average_price = (self.broker_asset.share_average_price_brl * self.broker_asset.shares_amount + self.shares_amount * self.share_cost_brl) / (self.broker_asset.shares_amount + self.shares_amount)
        if self.order == 'Buy':
            self.portfolio_asset.shares_amount += self.shares_amount
            self.portfolio_asset.share_average_price_brl = self.new_average_price
            self.broker_asset.shares_amount += self.shares_amount
            self.broker_asset.share_average_price_brl = self.broker_average_price
        if self.order == 'Sell':
            self.portfolio_asset.shares_amount -= self.shares_amount
        self.portfolio_asset.save()
        super(Transaction, self).save(*args, **kwargs) 
        self.broker_asset.save()
        super(Transaction, self).save(*args, **kwargs) 



    
    def __str__(self):
        return '{}'.format(self.portfolio_asset.asset.ticker)

    class Meta:
        verbose_name_plural = "  Transactions"




    # Atualiza valores no Portfolio Assets na atualização de ordens estudar depois

    # def delete(self, *args, **kwargs):
    #     self.portfolio_asset.shares_amount -= self.shares_amount
    #     self.portfolio_asset.save()
    #     super(Transaction, self).delete(*args, **kwargs) 

    # @receiver(pre_save, sender=Transaction)
    # def update_balance_account(sender, instance, update_fields=None, **kwargs):
    #     trans = Transaction.objects.get(portfolio_asset=instance.portfolio_asset, id=instance.id, UserID=instance.UserID)
    #     instance.portfolio_asset.shares_amount -= trans.shares_amount
    #     instance.portfolio_asset.save()





    