from django.db import models
from categories.models import Category, SubCategory
from common.models import Currency


class Asset(models.Model):
    category = models.ForeignKey(
        Category, related_name='categories', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        SubCategory, related_name='subcategories', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    price_usd = models.FloatField(default=0)
    price_brl = models.FloatField(default=0)

    dividend_frequency = models.FloatField(default=4)
    twelve_m_dividend = models.FloatField(default=0)
    p_vpa = models.FloatField(default=0)
    top_52w = models.FloatField(default=0)
    bottom_52w = models.FloatField(default=0)
    twelve_m_yield = models.FloatField(default=0)
    ranking = models.FloatField(default=0)
    is_radar = models.BooleanField(default=True)

    leveragedChoices = (
        ('Sim', 'Sim'),
        ('Não', 'Não'),
        ('Sem Classificação', 'Sem Classificação'),
    )
    is_leveraged = models.CharField(
        max_length=255, choices=leveragedChoices, default='Sem Classificação')
    leverage_percentage = models.FloatField(default=0)

    ideal_percentage = models.FloatField(default=0)

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
    ffo_yield = models.FloatField(default=0)
    p_ffo = models.FloatField(default=0)
    market_cap = models.FloatField(default=0)
    liquidity = models.FloatField(default=0)
    assets = models.FloatField(default=0)
    price_m2 = models.FloatField(default=0)
    rent_m2 = models.FloatField(default=0)
    cap_rate = models.FloatField(default=0)
    vacancy = models.FloatField(default=0)

    

    @property
    def p_ffo(self):
        try:
            return round(1 / (self.ffo_yield * 100), 2)
        except ZeroDivisionError:
            return 0


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


class CurrencyHolding(Asset):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1) 
    
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


class InternationalAssets(Asset):
    is_dividend_aristocrat = models.BooleanField(default=False)
    der = models.FloatField(default=0)
    ffo = models.FloatField(default=0)
    p_ffo = models.FloatField(default=0)
    earnings_yield = models.FloatField(default=0)
    roic = models.FloatField(default=0)
    ffo_yield = models.FloatField(default=0)

    class Meta:
        abstract = True


class Stocks(InternationalAssets):
    class Meta:
        verbose_name_plural = "Internacional / Stocks"


class Reit(InternationalAssets):
    class Meta:
        verbose_name_plural = "Internacional / REIT"


