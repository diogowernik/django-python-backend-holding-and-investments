from django.db import models
from investments.models import Asset

class CurrencyHistoricalPrice(models.Model):
    currency_pair = models.CharField(max_length=10)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    def __str__(self):
        return f"{self.currency.ticker} - {self.date} - {self.close}"
    

class AssetHistoricalPrice(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)  # BRL, USD, EUR
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    def __str__(self):
        return f"{self.asset.ticker} - {self.date} - {self.close} {self.currency}"