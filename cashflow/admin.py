from django.contrib import admin
from .models import InternationalCurrencyTransfer, CurrencyTransfer, CurrencyTransaction

# Depósito e Saques
class CurrencyTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'description',
                    'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)

    def save_model(self, request, obj, form, change):
        # Somente chame save() quando todos os campos necessários forem preenchidos
        if obj.portfolio and obj.broker and obj.transaction_type is not None and obj.transaction_amount is not None:
            super().save_model(request, obj, form, change)
# admin.site.register(CurrencyTransaction, CurrencyTransactionAdmin)

# Transferências entre contas

class CurrencyTransferAdmin(admin.ModelAdmin):
    list_display = (
        'transfer_date',
        'portfolio',
        'from_broker',
        'to_broker',
        'transfer_amount',
        'from_transaction',
        'to_transaction',
        )
    list_filter = (
        'portfolio',
        'from_broker',
        'to_broker',
        'from_transaction',
        'to_transaction',
        )
    search_fields = ['portfolio__name']

    def save_model(self, request, obj, form, change):
        # Somente chame save() quando todos os campos necessários forem preenchidos
        if obj.portfolio and obj.broker and obj.transaction_type is not None and obj.transaction_amount is not None:
            super().save_model(request, obj, form, change)
# admin.site.register(CurrencyTransfer, CurrencyTransferAdmin)


class InternationalCurrencyTransferAdmin(admin.ModelAdmin):
    list_display = (
        'transfer_date',
        'portfolio',
        'from_broker',
        'to_broker',
        'from_transfer_amount',
        'to_transfer_amount',
        'transfer_fee',
        'exchange_rate',
        'from_transaction',
        'to_transaction',
        )
    list_filter = (
        'portfolio',
        'from_broker',
        'to_broker',
        'from_transaction',
        'to_transaction',
        )
    search_fields = ['portfolio__name']

# admin.site.register(InternationalCurrencyTransfer, InternationalCurrencyTransferAdmin)

