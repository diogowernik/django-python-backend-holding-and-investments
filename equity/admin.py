from django.contrib import admin
from .models import QuotaHistory, SubscriptionEvent, PortfolioTotalHistory, RedemptionEvent, InvestBrEvent, DividendReceiveEvent, DividendPayEvent, ValuationEvent

from django import forms

class SubscriptionEventAdminForm(forms.ModelForm):
    class Meta:
        model = SubscriptionEvent
        exclude = ('transaction_type', 'price_brl', 'price_usd')
        labels = {
            'transaction_amount': 'Deposit R$',
        }
        help_texts = {
            'transaction_amount': 'obs: Esta operação cria um deposito e aumenta o numero de quotas.',
        }

class SubscriptionEventAdmin(admin.ModelAdmin):
    form = SubscriptionEventAdminForm
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)

admin.site.register(SubscriptionEvent, SubscriptionEventAdmin)

# Resgate - Diminuição de cotas
class RedemptionEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd')
admin.site.register(RedemptionEvent, RedemptionEventAdmin)

# Investir no Brasil 
class InvestBrEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd', 'transaction_amount')
admin.site.register(InvestBrEvent, InvestBrEventAdmin)

class DividendReceiveEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd')
admin.site.register(DividendReceiveEvent, DividendReceiveEventAdmin)

class DividendPayEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd')
admin.site.register(DividendPayEvent, DividendPayEventAdmin)

class ValuationEventAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'event_type', 'value_brl', 'value_usd', 
                    'total_brl', 'total_usd', 'quota_amount', 'quota_price_brl', 'quota_price_usd', 'percentage_change')
    list_filter = ('portfolio', 'date', 'event_type')
    search_fields = ('portfolio', 'date', 'event_type')
    ordering = ('-date',)
    exclude = ('event_type', 'value_brl', 'value_usd', 'total_brl', 'total_usd', 'quota_amount', 'quota_price_brl', 'quota_price_usd', 'percentage_change')
admin.site.register(ValuationEvent, ValuationEventAdmin)

# Historico de quotas
class QuotaHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'event_type', 'value_brl', 'value_usd', 
                    'total_brl', 'total_usd', 'quota_amount', 'quota_price_brl', 'quota_price_usd', 'percentage_change')
    list_filter = ('portfolio', 'date', 'event_type')
    search_fields = ('portfolio', 'date', 'event_type')
    ordering = ('-date',)
admin.site.register(QuotaHistory, QuotaHistoryAdmin)

# Histórico de totais
class PortfolioTotalHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'total_brl', 'total_usd')
    list_filter = ('portfolio', 'date')
    search_fields = ('portfolio', 'date')
    ordering = ('-date',)
admin.site.register(PortfolioTotalHistory, PortfolioTotalHistoryAdmin)