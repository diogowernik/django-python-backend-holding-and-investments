from django.contrib import admin
from .models import QuotaHistory, SubscriptionEvent, PortfolioTotalHistory, RedemptionEvent, InvestBrEvent, DividendReceiveEvent, ValuationEvent, TaxPayEvent, DivestBrEvent, InvestUsEvent, DivestUsEvent, PortfolioHistoryByCategory, SendMoneyEvent
from django.utils import formats

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

# Investir no Exterior
class InvestUsEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd', 'transaction_amount')
admin.site.register(InvestUsEvent, InvestUsEventAdmin)

# Resgate no Exterior
class DivestUsEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd', 'transaction_amount')
admin.site.register(DivestUsEvent, DivestUsEventAdmin)

class DivestBrEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_usd', 'transaction_amount')
admin.site.register(DivestBrEvent, DivestBrEventAdmin)

class DividendReceiveEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd')
admin.site.register(DividendReceiveEvent, DividendReceiveEventAdmin)

# class DividendPayEventAdmin(admin.ModelAdmin):
#     list_display = ('transaction_date', 'price_brl','price_usd',
#                     'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
#     list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
#     search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
#     readonly_fields = ('portfolio_investment',)
#     exclude = ('transaction_type', 'price_brl', 'price_usd')
# admin.site.register(DividendPayEvent, DividendPayEventAdmin)

class TaxPayEventAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'price_brl','price_usd',
                    'portfolio_investment', 'broker', 'transaction_type', 'transaction_amount', 'portfolio')
    list_filter = ('portfolio', 'broker', 'transaction_type', 'transaction_date')
    search_fields = ['portfolio__name', 'broker__name', 'transaction_type']
    readonly_fields = ('portfolio_investment',)
    exclude = ('transaction_type', 'price_brl', 'price_usd')
admin.site.register(TaxPayEvent, TaxPayEventAdmin)


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
    list_display = ('portfolio', 'formatted_date', 'event_type', 'formatted_value_brl', 
                    'formatted_value_usd', 'formatted_total_brl', 'formatted_total_usd', 'formatted_quota_amount', 
                    'formatted_quota_price_brl', 'formatted_quota_price_usd', 'formatted_percentage_change')
    list_filter = ('portfolio', 'date', 'event_type')
    search_fields = ('portfolio', 'date', 'event_type')
    ordering = ('-date',)

    def formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")
    formatted_date.admin_order_field = 'date'  
    formatted_date.short_description = 'Date'

    def formatted_percentage_change(self, obj):
            return "{:.2f}%".format(obj.percentage_change * 100)
    formatted_percentage_change.admin_order_field = 'percentage_change'  
    formatted_percentage_change.short_description = '% Change'

    def formatted_value_brl(self, obj):
        return format(obj.value_brl, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_value_brl.admin_order_field = 'value_brl'  
    formatted_value_brl.short_description = 'Value BRL'  

    def formatted_value_usd(self, obj):
        return format(obj.value_usd, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_value_usd.admin_order_field = 'value_usd'  
    formatted_value_usd.short_description = 'Value USD'  

    def formatted_total_brl(self, obj):
        return format(obj.total_brl, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_total_brl.admin_order_field = 'total_brl'  
    formatted_total_brl.short_description = 'Total BRL'  

    def formatted_total_usd(self, obj):
        return format(obj.total_usd, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_total_usd.admin_order_field = 'total_usd'  
    formatted_total_usd.short_description = 'Total USD'  

    def formatted_quota_amount(self, obj):
        return format(obj.quota_amount, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_quota_amount.admin_order_field = 'quota_amount'  
    formatted_quota_amount.short_description = 'Quota Amount'  

    def formatted_quota_price_brl(self, obj):
        return format(obj.quota_price_brl, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_quota_price_brl.admin_order_field = 'quota_price_brl'  
    formatted_quota_price_brl.short_description = 'Quota R$'  

    def formatted_quota_price_usd(self, obj):
        return format(obj.quota_price_usd, ',.2f').replace(",", "x").replace(".", ",").replace("x", ".")
    formatted_quota_price_usd.admin_order_field = 'quota_price_usd'  
    formatted_quota_price_usd.short_description = 'Quota U$'

admin.site.register(QuotaHistory, QuotaHistoryAdmin)

# Histórico de totais
class PortfolioTotalHistoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'total_brl', 'total_usd')
    list_filter = ('portfolio', 'date')
    search_fields = ('portfolio', 'date')
    ordering = ('-date',)
admin.site.register(PortfolioTotalHistory, PortfolioTotalHistoryAdmin)


class PortfolioHistoryByCategoryAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'category', 'date', 'total_brl', 'total_usd')
    list_filter = ('portfolio', 'category', 'date')
    search_fields = ('portfolio', 'category', 'date')
    ordering = ('-date', 'category',)
admin.site.register(PortfolioHistoryByCategory, PortfolioHistoryByCategoryAdmin)

class SendMoneyEventAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'from_broker', 'to_broker', 'from_transfer_amount', 'to_transfer_amount', 'transfer_fee', 'exchange_rate', 'transfer_date')
    list_filter = ('portfolio', 'from_broker', 'to_broker', 'transfer_date')
    search_fields = ('portfolio', 'from_broker', 'to_broker', 'transfer_date')
admin.site.register(SendMoneyEvent, SendMoneyEventAdmin)