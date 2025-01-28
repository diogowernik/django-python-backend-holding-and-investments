from django.contrib import admin
from . import models

class CurrencyHistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('id','currency_pair', 'date', 'open', 'high', 'low', 'close')
    list_filter = ('currency_pair',)
# admin.site.register(models.CurrencyHistoricalPrice, CurrencyHistoricalPriceAdmin)

class AssetHistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'currency', 'date', 'close')
    list_filter = ('asset', 'currency')
# admin.site.register(models.AssetHistoricalPrice, AssetHistoricalPriceAdmin)