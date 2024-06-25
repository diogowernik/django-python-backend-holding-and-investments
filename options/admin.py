from django.contrib import admin
from .models import Expiration, Call, Put, PortfolioCalls, PortfolioPuts

@admin.register(Expiration)
class ExpirationAdmin(admin.ModelAdmin):
    list_display = ('date',)
    search_fields = ('date',)

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('option_ticker', 'asset', 'expiration', 'price_brl', 'strike_price', 'option_type', 'premium_percentage')
    search_fields = ('option_ticker', 'asset__ticker')
    list_filter = ('option_type', 'expiration__date', 'asset__ticker')

@admin.register(Put)
class PutAdmin(admin.ModelAdmin):
    list_display = ('option_ticker', 'asset', 'expiration', 'price_brl', 'strike_price', 'option_type', 'premium_percentage')
    search_fields = ('option_ticker', 'asset__ticker')
    list_filter = ('option_type', 'expiration__date', 'asset__ticker')

@admin.register(PortfolioCalls)
class PortfolioCallsAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'option', 'status', 'quantity', 'price_brl', 'total_brl', 'collateral', 'total_profit_brl', 'profit_percentage')
    search_fields = ('portfolio__name', 'option__option_ticker')
    list_filter = ('status', 'option__expiration__date', 'portfolio__name')
    list_editable = ('status',)

@admin.register(PortfolioPuts)
class PortfolioPutsAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'option', 'status', 'quantity', 'price_brl', 'total_brl', 'collateral', 'total_profit_brl', 'profit_percentage')
    search_fields = ('portfolio__name', 'option__option_ticker')
    list_filter = ('status', 'option__expiration__date', 'portfolio__name')
    list_editable = ('status',)
