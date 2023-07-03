from django.contrib import admin
from .models import AssetTransaction, AssetAveragePrice, CurrencyAveragePrice, Income, Expense, InternationalCurrencyTransfer, CurrencyTransfer, CurrencyTransaction
from portfolios.models import PortfolioInvestment
# Income and Expenses
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'broker', 'date', 'description', 'amount')
    list_filter = ('portfolio', 'broker', 'date')
    search_fields = ['description']
admin.site.register(Income, IncomeAdmin)

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'broker', 'date', 'description', 'amount')
    list_filter = ('portfolio', 'broker', 'date')
    search_fields = ['description']
admin.site.register(Expense, ExpenseAdmin)

# Currency Transaction
class CurrencyTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)

    def save_model(self, request, obj, form, change):
        # Somente chame save() quando todos os campos necessários forem preenchidos
        if obj.portfolio and obj.broker and obj.transaction_type is not None and obj.transaction_amount is not None:
            super().save_model(request, obj, form, change)

admin.site.register(CurrencyTransaction, CurrencyTransactionAdmin)


# class CurrencyAveragePriceAdmin(admin.ModelAdmin):
#     list_display = ['portfolio_investment', 'share_average_price_brl', 'share_average_price_usd']
#     search_fields = ['portfolio_investment']
# admin.site.register(CurrencyAveragePrice, CurrencyAveragePriceAdmin)

# Asset Transaction and Average Price
class AssetTransactionAdmin(admin.ModelAdmin):
    list_display = ['portfolio_investment', 'broker', 'asset', 'transaction_amount', 'transaction_type', 'transaction_date', 'asset_price_brl', 'asset_price_usd']
    search_fields = ['portfolio_investment', 'broker', 'asset', 'transaction_type']
    list_filter = ['transaction_type']
admin.site.register(AssetTransaction, AssetTransactionAdmin)

# class AssetAveragePriceAdmin(admin.ModelAdmin):
#     list_display = ['portfolio_investment', 'share_average_price_brl', 'share_average_price_usd']
#     search_fields = ['portfolio_investment']
# admin.site.register(AssetAveragePrice, AssetAveragePriceAdmin)

# Currency Transfer and International Currency Transfer
class CurrencyTransferAdmin(admin.ModelAdmin):
    list_display = ('from_portfolio_investment', 'to_portfolio_investment', 'transfer_amount', 'transfer_date', 'transfer_fee')
    list_filter = ('from_portfolio_investment', 'to_portfolio_investment', 'transfer_date')
    search_fields = ['from_portfolio_investment__ticker', 'to_portfolio_investment__ticker']  
admin.site.register(CurrencyTransfer, CurrencyTransferAdmin)

class InternationalCurrencyTransferAdmin(admin.ModelAdmin):
    list_display = ('from_portfolio_investment', 'to_portfolio_investment', 'transfer_amount_in_source_currency', 'transfer_date', 'transfer_fee', 'exchange_rate')
    list_filter = ('from_portfolio_investment', 'to_portfolio_investment', 'transfer_date')
    search_fields = ['from_portfolio_investment__ticker', 'to_portfolio_investment__ticker']  
admin.site.register(InternationalCurrencyTransfer, InternationalCurrencyTransferAdmin)
