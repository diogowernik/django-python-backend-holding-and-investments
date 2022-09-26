
# Register your models here.

from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Minha Holding


# class AssetAdmin(admin.ModelAdmin):
#     list_display = ('ticker', 'price', 'category')
#     prepopulated_fields = {'slug': ('ticker',)}
#     list_editable = ['price', 'category']
#     list_filter = (('category', RelatedFieldListFilter),)
#     search_fields = ['ticker']


class FiiAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'ranking', 'subcategory', 'price', 'last_dividend',
                    'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'subcategory', 'last_dividend',
                     'last_yield', 'six_m_yield', 'p_vpa']
    list_filter = (('subcategory', RelatedFieldListFilter),)


# Ações Brasileiras

class BrStocksAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'ranking', 'subcategory', 'price',
                    'twelve_m_yield', 'ev_ebit', 'roic', 'pl', 'roe', 'p_vpa',
                    # 'ranking_all'
                    )
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'subcategory',
                     'ev_ebit', 'roic', 'pl', 'roe', 'p_vpa']
    list_filter = (('subcategory', RelatedFieldListFilter),)


class CryptoAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'slug', 'price', 'category', 'subcategory',
                    'marketcap', 'circulating_supply')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['slug', 'price', 'category', 'subcategory',
                     'marketcap', 'circulating_supply']


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


class FixedIncomeAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


class InvestmentFundsAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


class PrivateAssetAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', 'subcategory', ]


class StocksAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory',
                    'dividend_frequency', 'twelve_m_dividend', 'is_dividend_aristocrat')
    list_editable = ['price', 'category', 'subcategory',
                     'dividend_frequency', 'twelve_m_dividend', 'is_dividend_aristocrat']


class ReitAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category', 'subcategory',
                    'dividend_frequency', 'twelve_m_dividend', 'is_dividend_aristocrat')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', 'subcategory',
                     'dividend_frequency', 'twelve_m_dividend', 'is_dividend_aristocrat']


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
