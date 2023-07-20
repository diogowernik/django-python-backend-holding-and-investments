from django.contrib import admin
from .models import QuotaHistory

class QuotaHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'event_type', 'value_brl', 'value_usd', 
                    'total_brl', 'total_usd', 'quota_amount', 'quota_price_brl', 'quota_price_usd', 'percentage_change')
    list_filter = ('portfolio', 'date', 'event_type')
    search_fields = ('portfolio', 'date', 'event_type')
    ordering = ('-date',)

admin.site.register(QuotaHistory, QuotaHistoryAdmin)
