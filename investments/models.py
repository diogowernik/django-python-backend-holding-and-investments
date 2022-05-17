from django.db import models
from categories.models import Category, SetorFii, SetorCrypto


class Asset(models.Model):
    category = models.ForeignKey(
        Category, related_name='categories', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    price = models.FloatField()

    def __str__(self):
        return '{} | {}'.format(self.ticker, self.price)

    class Meta:
        verbose_name_plural = "  Assets"
        ordering = ('-ticker',)

# Child Classes with ihneritace from Assets


class Fii(Asset):
    setor_fii = models.ForeignKey(
        SetorFii, null=True, default=None, on_delete=models.CASCADE, related_name="setor_fiis")
    last_dividend = models.FloatField(default=0)
    last_yield = models.FloatField(default=0)
    six_m_yield = models.FloatField(default=0)
    twelve_m_yield = models.FloatField(default=0)
    p_vpa = models.FloatField(default=0)

    def __str__(self):
        return '{}'.format(self.ticker)

    class Meta:
        verbose_name_plural = "  Brazilian Reits"


class Stocks(Asset):

    class Meta:
        verbose_name_plural = "   Stocks"


class Currency(Asset):
    class Meta:
        verbose_name_plural = " Currencies"


class FixedIncome(Asset):
    default_currency = models.ForeignKey(
        Currency, related_name='currencies', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "    Fixed Incomes"


class Crypto(Asset):
    setor_crypto = models.ForeignKey(
        SetorCrypto, null=True, default=1, on_delete=models.CASCADE, related_name="setor_cryptos")
    marketcap = models.FloatField(default=0)
    circulating_supply = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Cripto Currencies"


class PrivateAsset(Asset):
    class Meta:
        verbose_name_plural = "  Private Assets"
