
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
    list_display = ('ticker', 'setor_fii', 'price', 'last_dividend',
                    'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'setor_fii', 'last_dividend',
                     'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa']


class StocksAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category')


class CryptoAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'slug', 'price', 'category',
                    'setor_crypto', 'marketcap', 'circulating_supply')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['slug', 'price', 'category', 'setor_crypto',
                     'marketcap', 'circulating_supply']


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


class FixedIncomeAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


class PrivateAssetAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'category')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', ]


# admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Fii, FiiAdmin)
admin.site.register(models.Stocks, StocksAdmin)
admin.site.register(models.Crypto, CryptoAdmin)
admin.site.register(models.Currency, CurrencyAdmin)
admin.site.register(models.FixedIncome, FixedIncomeAdmin)
admin.site.register(models.PrivateAsset, PrivateAssetAdmin)
