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
    list_display =('asset', 'portfolio', 'broker', 'shares_amount', 'share_average_price_brl', 'total_cost_brl', 'total_today_brl' )
    list_editable = ['portfolio', 'broker', 'shares_amount', 'share_average_price_brl', 'total_cost_brl', 'total_today_brl']
    list_filter =(('broker', RelatedFieldListFilter), ('portfolio', RelatedFieldListFilter),)

admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.PortfolioAsset, PortfolioAssetAdmin)
