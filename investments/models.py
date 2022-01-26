


# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelState  # default user from django
from django.urls import reverse

# Main

class AssetManager(models.Manager):
    def get_queryset(self):
        return super(AssetManager, self).get_queryset().filter(is_active=True)

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)
    
    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])
    
    class Meta:
        verbose_name_plural = "   Categories" # Espaços em Branco organizam quem vem primeiro
    

class Asset(models.Model):
    category = models.ForeignKey(Category, related_name='asset', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(max_digits=18, decimal_places=18)
    objects = models.Manager()
    assets = AssetManager()

    def __str__(self):
        return '  {}  |  {}  |  {}  '.format(self.ticker, self.price, self.category)

    class Meta:
        verbose_name_plural = "  Assets"
        ordering = ('-ticker',)

    def get_absolute_url(self):
        return reverse('store:asset_detail', args=[self.slug])
    

# Child Classes with ihneritace from Assets
class Fii(Asset):
    setor = models.CharField(max_length=255)
    last_dividend = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_yield = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    six_m_yield = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    twelve_m_yield = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    p_vpa = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    def __str__(self):
        return '  {}  |  {}  |  {}  '.format(self.ticker, self.price, self.setor)
    
    class Meta:
        verbose_name_plural = " Fiis"
        
class Stock(Asset):
    setor = models.CharField(max_length=255)
    twelve_m_yield = models.DecimalField(max_digits=18, decimal_places=2)
    p_vpa = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        verbose_name_plural = " Stocks"

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends")
    value_per_share_brl = models.DecimalField(max_digits=18, decimal_places=2)
    record_date = models.DateField(null=True, blank=True)
    pay_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividends"


        

    

