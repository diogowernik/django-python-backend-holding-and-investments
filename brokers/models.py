from django.db import models

# Create your models here.

class Currency(models.Model):
    ticker = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price_brl = models.FloatField(default=0)
    price_usd = models.FloatField(default=0)

    def __str__(self):
        return f"{self.ticker} - {self.price_brl} - {self.price_usd}"

class CurrencyHistoricalPrice(models.Model):
    currency_pair = models.CharField(max_length=10)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    def __str__(self):
        return f"{self.currency.ticker} - {self.date} - {self.close}"


class Broker(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    tax_brl = models.FloatField(default=0.0)
    tax_usd = models.FloatField(default=0.0)
    tax_percent = models.FloatField(default=0.0)
    main_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = " Brokers"
