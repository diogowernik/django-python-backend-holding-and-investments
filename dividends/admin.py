from django.contrib import admin
from . import models

# Register your models here.


class DividendAdmin(admin.ModelAdmin):
    list_display = ('asset', 'value_per_share_usd', 
                    'value_per_share_brl', 'record_date', 'pay_date')
    list_editable = ('value_per_share_usd', 
                     'value_per_share_brl', 'record_date', 'pay_date')
    list_filter = ('record_date', 'pay_date')

    # search_fields = ('asset__ticker', 'asset__name')


admin.site.register(models.Dividend, DividendAdmin)

class PortfolioDividendAdmin(admin.ModelAdmin):
    list_display = ('portfolio_investment', 'asset', 'category', 'record_date', 'pay_date', 'shares_amount', 'value_per_share_brl', 'value_per_share_usd', 'average_price_brl', 'average_price_usd')

admin.site.register(models.PortfolioDividend, PortfolioDividendAdmin)

class TransactionsHistoryAdmin(admin.ModelAdmin):
    list_display = ( 'timestamp',
        'portfolio_investment', 'transaction', 'share_average_price_brl', 'share_average_price_usd', 'total_shares', 'total_brl', 'total_usd',)

admin.site.register(models.TransactionsHistory, TransactionsHistoryAdmin)