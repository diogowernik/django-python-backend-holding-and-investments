from django.contrib import admin
from . import models

# Register your models here.


class DividendAdmin(admin.ModelAdmin):
    list_display = ('asset', 'value_per_share_usd', 'value_per_share_brl', 'record_date_date', 'pay_date_date')
    list_filter = ('record_date', 'pay_date')
    search_fields = ('asset__ticker', )

    def record_date_date(self, obj):
        return obj.record_date.strftime('%d/%m/%Y')
    def pay_date_date(self, obj):
        return obj.pay_date.strftime('%d/%m/%Y')
    
admin.site.register(models.Dividend, DividendAdmin)

class PortfolioDividendAdmin(admin.ModelAdmin):
    list_display = ('portfolio_investment', 'asset',  'record_date', 'pay_date', 'shares_amount', 'value_per_share_brl', 'value_per_share_usd', 'average_price_brl', 'average_price_usd')
admin.site.register(models.PortfolioDividend, PortfolioDividendAdmin)

