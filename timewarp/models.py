from django.db import models

class CurrencyHistoricalPrice(models.Model):
    currency_pair = models.CharField(max_length=10)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    def __str__(self):
        return f"{self.currency.ticker} - {self.date} - {self.close}"