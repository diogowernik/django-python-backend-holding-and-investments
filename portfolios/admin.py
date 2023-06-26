from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from django import forms

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
    list_display = (
        'asset',
        'is_radar',
        'broker',
        'shares_amount',
        'share_average_price_brl',
        'total_cost_brl',
        'share_average_price_usd',
        'total_cost_usd',
        'total_today_brl',
        'total_today_usd',
        'trade_profit_brl',
        'trade_profit_usd',
        'div_profit_brl',
        'div_profit_usd',
        'total_profit_brl',
        'portfolio',
        'category'
    )
    list_filter = [
        ('broker', RelatedFieldListFilter), ('portfolio', RelatedFieldListFilter), 'asset__category', ]

    # override dividend_profit_brl and dividend_profit_usd to round the values

    def div_profit_brl(self, obj):
        return round(obj.dividends_profit_brl, 2)

    def div_profit_usd(self, obj):
        return round(obj.dividends_profit_usd, 2)

    def get_changelist(self, request):
        return PortfolioInvestmentSum


class PortfolioTradeAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'asset',
        'category',
        'order',
        'broker',
        'shares_amount',

        'share_cost_brl',
        'total_cost_brl',
        'tax_brl',

        'share_cost_usd',
        'total_cost_usd',
        'tax_usd',

        'usd_on_date',
        'portfolio'
    )
    list_editable = [
        'broker',
        'category',
    ]
    list_filter = (
        ('broker', RelatedFieldListFilter),
        ('portfolio', RelatedFieldListFilter),
        ('broker', RelatedFieldListFilter),
        'category',
        'asset',
    )


class PortfolioDividendAdmin(admin.ModelAdmin):
    list_display = (
        'ticker',
        'category',
        'subcategory',
        'record_date',
        'pay_date',
        'shares_amount',
        'value_per_share_usd',
        'value_per_share_brl',
        'total_dividend_brl',
        'total_dividend_usd',
        'average_price_usd',
        'average_price_brl',
        'usd_on_pay_date',
        'yield_brl',
        'yield_usd'
    )
    # list_editable = ['shares_amount', 'value_per_share_usd', 'value_per_share_brl',
    #                  'average_price_usd', 'average_price_brl', 'usd_on_pay_date']

    # filter by portfolio
    list_filter = (
        ('portfolio', RelatedFieldListFilter),
        'category',
        'subcategory',
    )

    def yield_brl(self, obj):
        return str(format(float(obj.yield_on_cost_brl * 100), '.2f') + '%')

    def yield_usd(self, obj):
        return str(format(float(obj.yield_on_cost_usd * 100), '.2f') + '%')


class PortfolioHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'asset',
        'order',

        'shares_amount',
        'total_shares',

        'share_cost_brl',
        'share_average_price_brl',
        'total_cost_brl',
        'total_on_date_brl',
        'tax_brl',
        'trade_profit_brl',

        # 'share_cost_usd',
        # 'share_average_price_usd',
        # 'total_cost_usd',
        # 'total_on_date_usd',
        # 'tax_usd',
        # 'trade_profit_usd'

    )
    list_filter = (
        ('portfolio', RelatedFieldListFilter),
        'asset',
    )

#     def profit_percentage(self, obj):
#         return str(format(float(obj.profit * 100), '.2f') + ' %')

#     def historical_percentage(self, obj):
#         return str(format(float(obj.historical_profit * 100), '.2f') + ' %')


class PortfolioEvolutionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'portfolio',
        'category',
        'category_total_brl',
        'category_total_usd')
    list_editable = ['category', 'category_total_brl',
                     'category_total_usd']
    list_filter = (
        ('portfolio', RelatedFieldListFilter),
    )


# admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.PortfolioInvestment, PortfolioInvestmentAdmin)
admin.site.register(models.PortfolioTrade, PortfolioTradeAdmin)
admin.site.register(models.PortfolioHistory, PortfolioHistoryAdmin)
admin.site.register(models.PortfolioDividend, PortfolioDividendAdmin)
admin.site.register(models.PortfolioEvolution, PortfolioEvolutionAdmin)
