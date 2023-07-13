from django.contrib import admin
from .models import Trade, TradeCalculation, TradeHistory



# Compra e Venda de Ativos
class TradeAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
admin.site.register(Trade, TradeAdmin)

# Compra e Venda / Histórico
@admin.register(TradeHistory)
class TradeHistoryAdmin(admin.ModelAdmin):
    list_display = ( 'transaction_date',
        'portfolio_investment', 'transaction', 'share_average_price_brl', 'share_average_price_usd', 'total_shares', 'total_brl', 'total_usd',)

# Compra e Venda / Cálculo
@admin.register(TradeCalculation)
class TradeCalculationAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'portfolio_investment', 'share_average_price_brl', 'share_average_price_usd', 'total_shares', 'total_brl', 'total_usd',)


