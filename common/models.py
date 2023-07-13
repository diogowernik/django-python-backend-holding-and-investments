from django.db import models

# adicionar uma ação que quando é atualizado, atualiza CurrencyHoldings
class Currency(models.Model):
    ticker = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price_brl = models.FloatField(default=0)
    price_usd = models.FloatField(default=0)

    def __str__(self):
        return f"{self.ticker} - {self.price_brl} - {self.price_usd}"