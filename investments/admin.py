
# Register your models here.

from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Minha Holding


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticker', 'price_brl', 'price_usd', 'category', 'subcategory',
                    'twelve_m_dividend', 'twelve_m_yield', 'p_vpa', 'top_52w', 'bottom_52w')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['category', 'subcategory', 'twelve_m_dividend',
                     'twelve_m_yield', 'p_vpa', 'top_52w', 'bottom_52w']
    list_filter = (('category', RelatedFieldListFilter),)
    search_fields = ['ticker']


class FiiAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class BrStocksAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class CryptoAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class CurrencyAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class FixedIncomeAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class InvestmentFundsAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class PrivateAssetAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class StocksAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


class ReitAdmin(AssetAdmin):
    list_filter = (('subcategory', RelatedFieldListFilter),)


# admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Fii, FiiAdmin)
admin.site.register(models.Stocks, StocksAdmin)
admin.site.register(models.Crypto, CryptoAdmin)
admin.site.register(models.Currency, CurrencyAdmin)
admin.site.register(models.FixedIncome, FixedIncomeAdmin)
admin.site.register(models.InvestmentFunds, InvestmentFundsAdmin)
admin.site.register(models.PrivateAsset, PrivateAssetAdmin)
admin.site.register(models.BrStocks, BrStocksAdmin)
admin.site.register(models.Reit, ReitAdmin)
admin.site.register(models.Asset, AssetAdmin)
