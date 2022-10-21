from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Sum


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_editable = ['owner']


class PortfolioInvestmentSum(ChangeList):
    def get_results(self, *args, **kwargs):
        super(PortfolioInvestmentSum, self).get_results(*args, **kwargs)
        if self.result_list:
            q = self.result_list.aggregate(
                portfolio_asset_sum=Sum('total_today_brl'))
            self.portfolio_asset_sum = round(q['portfolio_asset_sum'], 2)


class PortfolioInvestmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'broker', 'shares_amount', 'share_average_price_brl', 'total_cost_brl', 'share_average_price_usd', 'total_cost_usd',
                    'total_today_brl', 'total_today_usd', 'trade_profit_brl', 'trade_profit_usd', 'dividends_profit_brl', 'dividends_profit_usd',
                    'total_profit_brl', 'portfolio', 'category')
    # list_editable = ['shares_amount', 'share_average_price_usd', 'share_average_price_brl',
    #                  'portfolio', 'broker']
    list_filter = [
        ('broker', RelatedFieldListFilter), ('portfolio', RelatedFieldListFilter), ]

    def get_changelist(self, request):
        return PortfolioInvestmentSum


class PortfolioTradeAdmin(admin.ModelAdmin):
    list_display = ('date',  'asset', 'order', 'broker', 'shares_amount',
                    'share_cost_brl', 'total_cost_brl', 'total_cost_usd',  'portfolio')
    # list_editable = ['broker']
    list_filter = (('broker', RelatedFieldListFilter),
                   ('portfolio', RelatedFieldListFilter),)


class PortfolioDividendAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'category', 'subcategory', 'record_date', 'pay_date', 'shares_amount', 'value_per_share_usd',
                    'value_per_share_brl', 'total_dividend_brl', 'total_dividend_usd', 'average_price_usd', 'average_price_brl', 'yield_on_cost',
                    'usd_on_pay_date')
    # filter by portfolio
    list_filter = (('portfolio', RelatedFieldListFilter),
                   'category', 'subcategory',)


class PortfolioHistoryAdmin(admin.ModelAdmin):
    list_display = ('date', 'portfolio', 'total_today_brl', 'total_today_usd', 'order_value',
                    'tokens_amount', 'token_price', 'profit_percentage', 'historical_percentage')
    list_filter = (('portfolio', RelatedFieldListFilter),)

    def profit_percentage(self, obj):
        # Return the profit as percentage string
        return str(format(float(obj.profit * 100), '.2f') + ' %')

    def historical_percentage(self, obj):
        # Return the profit as percentage string
        return str(format(float(obj.historical_profit * 100), '.2f') + ' %')


# admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.PortfolioInvestment, PortfolioInvestmentAdmin)
admin.site.register(models.PortfolioTrade, PortfolioTradeAdmin)
admin.site.register(models.PortfolioHistory, PortfolioHistoryAdmin)
admin.site.register(models.PortfolioDividend, PortfolioDividendAdmin)
