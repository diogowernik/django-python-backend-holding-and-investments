from django.db import models
from numpy import product
from categories.models import Category, SetorFii, SetorCrypto, SetorBrStocks


class Asset(models.Model):
    category = models.ForeignKey(
        Category, related_name='categories', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    price = models.FloatField(default=0)

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
    ranking = models.FloatField(default=0)

    def __str__(self):
        return '{}'.format(self.ticker)

    class Meta:
        verbose_name_plural = "  Brazilian Reits"


class Stocks(Asset):

    class Meta:
        verbose_name_plural = "   Stocks"


class BrStocks(Asset):
    setor_br_stocks = models.ForeignKey(
        SetorBrStocks, null=True, default=None, on_delete=models.CASCADE, related_name="setor_br_stocks")
    twelve_m_yield = models.FloatField(default=0)
    ev_ebit = models.FloatField(default=0)
    roic = models.FloatField(default=0)
    pl = models.FloatField(default=0)
    roe = models.FloatField(default=0)
    p_vpa = models.FloatField(default=0)
    ranking = models.FloatField(default=0)
    ranking_all = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "   Brazilian Stocks"


class Currency(Asset):
    class Meta:
        verbose_name_plural = " Currencies"


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
        verbose_name_plural = "    Fixed Incomes"

    def __str__(self):
        return '{} | {}'.format(self.ticker, self.deadline)


class InvestmentFunds(Asset):
    ambima_code = models.CharField(max_length=255, unique=True)
    twelve_m_profit = models.FloatField(default=0)
    liquidity = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "    Investment Funds"


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
