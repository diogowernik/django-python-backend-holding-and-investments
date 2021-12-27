from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Portfolio)

class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display =('asset', 'portfolio', 'shares_amount', 'share_average_price_brl', 'total_cost_brl', 'total_today_brl' )

admin.site.register(models.PortfolioAsset, PortfolioAssetAdmin)
