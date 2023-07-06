from django.contrib import admin
from .models import AssetTransaction, AssetAveragePrice, CurrencyAveragePrice,  InternationalCurrencyTransfer, CurrencyTransfer, CurrencyTransaction
from portfolios.models import PortfolioInvestment

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

class AssetTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
admin.site.register(AssetTransaction, AssetTransactionAdmin)

