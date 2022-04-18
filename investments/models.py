

# Create your models here.

from django.db import models

# Main


class SetorFii(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "   Setor Fiis"  # White spaces organize who comes first


class SetorCrypto(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = "   Setor Cryptos"


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "   Categories"  # White spaces organize who comes first


class Asset(models.Model):
    category = models.ForeignKey(
        Category, related_name='categories', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    price = models.FloatField()

    def __str__(self):
        return '{}'.format(self.ticker)

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
        verbose_name_plural = " Fiis"


class ETF(Asset):

    class Meta:
        verbose_name_plural = " ETFs"


class Currency(Asset):
    class Meta:
        verbose_name_plural = " Currencies"


class FixedIncome(Asset):
    default_currency = models.ForeignKey(
        Currency, related_name='currencies', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = " RendaFixas"


class Crypto(Asset):
    setor_crypto = models.ForeignKey(
        SetorCrypto, null=True, default=1, on_delete=models.CASCADE, related_name="setor_cryptos")
    marketcap = models.FloatField(default=0)
    circulating_supply = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = " Crytpos"


class PrivateAsset(Asset):
    class Meta:
        verbose_name_plural = " Private Assets"


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
