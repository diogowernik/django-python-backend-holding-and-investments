from django.db import models
from investments.models import Asset
# Create your models here.


class Dividend(models.Model):
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="dividends")
    value_per_share_brl = models.FloatField()
    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividends"
