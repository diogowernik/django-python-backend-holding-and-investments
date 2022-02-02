from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Register your models here.

class PortfolioAdmin(admin.ModelAdmin):
    list_display =('name', 'owner')
    list_editable = ['owner']
    
class BrokerAdmin(admin.ModelAdmin):
    list_display =('name', 'slug' )
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']

class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display =('asset', 'shares_amount', 'share_average_price_brl','total_cost_brl', 'total_today_brl', 'profit' )
    list_editable = ['shares_amount', 'share_average_price_brl']
    list_filter =(('portfolio', RelatedFieldListFilter),)

admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.PortfolioAsset, PortfolioAssetAdmin)
