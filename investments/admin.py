
# Register your models here.

from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Minha Holding

admin.site.register(models.Category)


class AssetAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category']
    list_filter =(('category', RelatedFieldListFilter),)

class FiiAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category', 'setor', 'last_dividend', 'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa' )
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', 'setor', 'last_dividend', 'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa']

class ETFAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category')

class CryptoAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category', 'setor', 'marketcap', 'circulating_supply' )
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['price', 'category', 'setor', 'marketcap', 'circulating_supply']

class DividendAdmin(admin.ModelAdmin):
    list_display =('asset', 'value_per_share_brl', 'record_date', 'pay_date' )
# Como puxar valores da tabela foreing key

admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Fii, FiiAdmin )
admin.site.register(models.ETF, ETFAdmin)
admin.site.register(models.Crypto, CryptoAdmin)
admin.site.register(models.Dividend, DividendAdmin)