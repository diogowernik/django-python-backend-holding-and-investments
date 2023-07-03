from django.contrib import admin
from . import models

# Register your models here.


class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_currency', 'slug', 'tax_brl', 'tax_usd', 'tax_percent')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug', 'tax_brl', 'tax_usd', 'tax_percent', 'main_currency']

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'slug', 'name', 'price_brl', 'price_usd')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['slug', 'price_brl', 'price_usd']


admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.Currency, CurrencyAdmin)
