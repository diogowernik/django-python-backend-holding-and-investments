from email.policy import default
from django.db import models
from investments.models import Asset
from django.core.exceptions import ValidationError
# Create your models here.


class Dividend(models.Model):
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="dividends")
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)

    groupChoices = (
        ('Dividend', 'Dividend'),
        ('DividendTax', 'Dividend Tax'),
    )
    group = models.CharField(
        max_length=255, choices=groupChoices, default='Dividend')

    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self.__class__.objects.\
                filter(asset=self.asset, pay_date=self.pay_date, group=self.group, value_per_share_usd=self.value_per_share_usd).\
                exclude(id=self.id).\
                exists():
            # except pass
            raise ValidationError(
                message='This dividend already exists.',
            )

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos por ativo"
