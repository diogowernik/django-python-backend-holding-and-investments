from django.contrib import admin
from .models import QuotaHistory, SubscriptionEvent, PortfolioHistory

class QuotaHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'event_type', 'value_brl', 'value_usd', 
                    'total_brl', 'total_usd', 'quota_amount', 'quota_price_brl', 'quota_price_usd', 'percentage_change')
    list_filter = ('portfolio', 'date', 'event_type')
    search_fields = ('portfolio', 'date', 'event_type')
    ordering = ('-date',)

admin.site.register(QuotaHistory, QuotaHistoryAdmin)


class SubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)

admin.site.register(SubscriptionEvent, SubscriptionEventAdmin)  

class PortfolioHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'total_brl', 'total_usd')
    list_filter = ('portfolio', 'date')
    search_fields = ('portfolio', 'date')
    ordering = ('-date',)
admin.site.register(PortfolioHistory, PortfolioHistoryAdmin)