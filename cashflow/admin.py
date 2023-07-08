from django.contrib import admin
from .models import AssetTransaction, AssetTransactionCalculation, CurrencyTransactionCalculation,  InternationalCurrencyTransfer, CurrencyTransfer, CurrencyTransaction, TransactionsHistory
from portfolios.models import PortfolioInvestment

# Depósito e Saques
class CurrencyTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)

    def save_model(self, request, obj, form, change):
        # Somente chame save() quando todos os campos necessários forem preenchidos
        if obj.portfolio and obj.broker and obj.transaction_type is not None and obj.transaction_amount is not None:
            super().save_model(request, obj, form, change)
admin.site.register(CurrencyTransaction, CurrencyTransactionAdmin)

# Compra e Venda de Ativos
class AssetTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
admin.site.register(AssetTransaction, AssetTransactionAdmin)

# Compra e Venda / Histórico
@admin.register(TransactionsHistory)
class TransactionsHistoryAdmin(admin.ModelAdmin):
    list_display = ( 'transaction_date',
        'portfolio_investment', 'transaction', 'share_average_price_brl', 'share_average_price_usd', 'total_shares', 'total_brl', 'total_usd',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Apenas para visualização
# Depósito e Saques / Calculos
# @admin.register(CurrencyTransactionCalculation)
# class CurrencyTransactionCalculationAdmin(admin.ModelAdmin):
#     list_display = ('portfolio_investment', 'share_average_price_brl', 'share_average_price_usd',)

#     def has_add_permission(self, request):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

# # Apenas para visualização
# Compra e Venda / Calculos
# @admin.register(AssetTransactionCalculation)
# class AssetTransactionCalculationAdmin(admin.ModelAdmin):
#     list_display = ('transaction_date', 'portfolio_investment', 'share_average_price_brl', 'share_average_price_usd', 'total_shares', 'total_brl', 'total_usd',)
    
#     def has_add_permission(self, request):
#         return False
    
#     def has_delete_permission(self, request, obj=None):
#         return False
    
#     def has_change_permission(self, request, obj=None):
#         return False



