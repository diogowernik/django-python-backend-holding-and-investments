from django.db import models
from django.contrib.auth.models import User
from investments.models import Asset

# Create your models here.

# Portfolios that belongs to User

class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)
    
    class Meta:
        verbose_name_plural = "   Portfolios"

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    shares_amount = models.DecimalField(max_digits=18, decimal_places=2) 
    share_average_price_brl = models.DecimalField(max_digits=18, decimal_places=2)
    total_cost_brl = models.DecimalField(max_digits=18, decimal_places=2)
    total_today_brl = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.shares_amount, self.share_average_price_brl, self.total_cost_brl)

    class Meta:
        verbose_name_plural = "  Portfolio Assets"

# class PortfolioOrder():
#     portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE)
#     shares_amount = models.DecimalField(max_digits=18, decimal_places=2)
#     share_cost_brl = models.DecimalField(max_digits=18, decimal_places=2)
#     total_cost_brl = models.DecimalField(max_digits=18, decimal_places=2)
#     order_type = [Buy, Sell]
#     date = 
