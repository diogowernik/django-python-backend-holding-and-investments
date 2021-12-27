
# Register your models here.

from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Minha Holding

admin.site.register(models.Category)


class AssetAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category')
    list_filter =(('category', RelatedFieldListFilter),)

class FiiAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category', 'setor', 'last_dividend', 'last_yield', 'six_m_yield', 'twelve_m_yield', 'p_vpa' )

class StockAdmin(admin.ModelAdmin):
    list_display =('ticker', 'price', 'category', 'setor', 'twelve_m_yield', 'p_vpa' )

class DividendAdmin(admin.ModelAdmin):
    list_display =('asset', 'value_per_share_brl', 'record_date', 'pay_date' )
# Como puxar valores da tabela foreing key

admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Fii, FiiAdmin )
admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.Dividend, DividendAdmin)