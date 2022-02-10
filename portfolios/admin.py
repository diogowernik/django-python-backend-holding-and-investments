from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models
from admin_auto_filters.filters import AutocompleteFilter


class PortfolioAdmin(admin.ModelAdmin):
    list_display =('name', 'owner')
    list_editable = ['owner']
    
class BrokerAdmin(admin.ModelAdmin):
    list_display =('name', 'slug' )
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']

class AssetFilter(AutocompleteFilter):
    title = 'Asset' # display title
    field_name = 'asset' # name of the foreign key field

class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display =('asset', 'shares_amount', 'share_average_price_brl','total_cost_brl', 'total_today_brl', 'profit', 'category' )
    list_editable = ['shares_amount', 'share_average_price_brl']
    # list_filter =(('asset__category', RelatedFieldListFilter),)
    list_filter = [AssetFilter, ('asset__category', RelatedFieldListFilter),]

class BrokerAssetAdmin(admin.ModelAdmin):
    list_display =('ticker', 'broker', 'shares_amount', 'share_average_price_brl','total_cost_brl', 'total_today_brl' )
    list_editable = ['shares_amount', 'broker', 'share_average_price_brl']
    list_filter =(('portfolio_asset__asset__category', RelatedFieldListFilter), ('broker', RelatedFieldListFilter),)

class TransactionAdmin(admin.ModelAdmin):
    list_display =('date','portfolio','asset','shares_amount', 'share_cost_brl','total_cost_brl', 'order', 'portfolio_avarage_price' )
    list_editable =                  ['shares_amount', 'share_cost_brl', 'order']
    list_filter =(('portfolio_asset__asset__category', RelatedFieldListFilter),)

admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.PortfolioAsset, PortfolioAssetAdmin)
admin.site.register(models.BrokerAsset, BrokerAssetAdmin)
admin.site.register(models.Transaction,TransactionAdmin)
