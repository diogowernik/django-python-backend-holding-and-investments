from django.db import models
from common.models import Currency

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
