from django.contrib import admin
from . import models

# Register your models here.


class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_currency','slug', 'tax_brl', 'tax_usd', 'tax_percent')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug', 'main_currency', 'tax_brl', 'tax_usd', 'tax_percent']


admin.site.register(models.Broker, BrokerAdmin)
