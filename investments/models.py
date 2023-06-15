from multiprocessing import set_forkserver_preload
from django.db import models
from numpy import product
from categories.models import Category, SubCategory


class Asset(models.Model):
    category = models.ForeignKey(
        Category, related_name='categories', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        SubCategory, related_name='subcategories', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    dividend_frequency = models.FloatField(default=4)
    twelve_m_dividend = models.FloatField(default=0)
    p_vpa = models.FloatField(default=0)
    top_52w = models.FloatField(default=0)
    bottom_52w = models.FloatField(default=0)
    twelve_m_yield = models.FloatField(default=0)
    ranking = models.FloatField(default=0)

    price_usd = models.FloatField(default=0)
    price_brl = models.FloatField(default=0)

    is_radar = models.BooleanField(default=True)

    def __str__(self):
        return '{} | {} | {}'.format(self.ticker, self.price_brl, self.price_usd)

    class Meta:
        verbose_name_plural = "Assets"
        ordering = ('-ticker',)

    @property
    def percentage_top_52w(self):
      # if zero division error, return 0
        try:
            return round((self.price_brl - self.top_52w) / self.top_52w * 100, 2)
        except ZeroDivisionError:
            return 0

    def percentage_bottom_52w(self):
        try:
            return round((self.price_brl - self.bottom_52w) / self.bottom_52w * 100, 2)
        except ZeroDivisionError:
            return 0


# Child Classes with ihneritace from Assets


class Fii(Asset):
    last_dividend = models.FloatField(default=0)
    last_yield = models.FloatField(default=0)
    six_m_yield = models.FloatField(default=0)

    def __str__(self):
        return '{}'.format(self.ticker)

    class Meta:
        verbose_name_plural = " Fundos Imobiliários"


class BrStocks(Asset):
    ev_ebit = models.FloatField(default=0)
    roic = models.FloatField(default=0)
    pl = models.FloatField(default=0)
    roe = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = " Ações Brasileiras"


class Currency(Asset):
    class Meta:
        verbose_name_plural = "Internacional / Moedas"


class FixedIncome(Asset):
    kindChoices = (
        ('Pre-Fixado', 'Pre-Fixado'),
        ('Pos-Fixado', 'Pos-Fixado'),
        ('Misto', 'Misto'),
    )
    indexerChoises = (
        ('IPCA', 'IPCA'),
        ('CDI', 'CDI'),
        ('Selic', 'Selic'),
        ('IGPM', 'IGPM'),
    )
    creditChoices = (
        ('Bancario', 'Bancario'),
        ('Soberano', 'Soberano'),
        ('Privado', 'Privado'),
    )
    kind = models.CharField(
        max_length=255, choices=kindChoices, default='Pre-Fixado')
    indexer = models.CharField(
        max_length=255, choices=indexerChoises, default='IPCA')
    credit_type = models.CharField(
        max_length=255, choices=creditChoices, default='Bancario')
    issuer = models.CharField(max_length=255, default='')
    interest_rate = models.FloatField(default=0)
    is_Ir = models.BooleanField(default=False)
    deadline = models.DateField(default=None, null=True)

    class Meta:
        verbose_name_plural = " Renda Fixa"

    def __str__(self):
        return '{} | {}'.format(self.ticker, self.deadline)


class InvestmentFunds(Asset):
    ambima_code = models.CharField(max_length=255, unique=True)
    twelve_m_profit = models.FloatField(default=0)
    liquidity = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = " Fundos de Investimentos"


class Crypto(Asset):
    marketcap = models.FloatField(default=0)
    circulating_supply = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Internacional / Criptomoedas"


class PrivateAsset(Asset):
    class Meta:
        verbose_name_plural = "Patrimônio Particular"

# class InternationalAssets abstract class


class InternationalAssets(Asset):
    is_dividend_aristocrat = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Stocks(InternationalAssets):
    class Meta:
        verbose_name_plural = "Internacional / Stocks"


class Reit(InternationalAssets):
    class Meta:
        verbose_name_plural = "Internacional / REIT"
