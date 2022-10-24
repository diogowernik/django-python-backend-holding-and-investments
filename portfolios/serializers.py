from rest_framework import serializers
from . import models
from investments.models import Category, Asset, Fii

# Minha Holding


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image')


class PortfolioDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image')


class PortfolioInvestmentSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='asset.category.name')
    subcategory = serializers.CharField(source='asset.subcategory.name')
    broker = serializers.CharField(source='broker.name')
    asset_price_brl = serializers.FloatField(source='asset.price_brl')
    asset_price_usd = serializers.FloatField(source='asset.price_usd')
    twelve_m_dividend = serializers.FloatField(
        source='asset.twelve_m_dividend')
    twelve_m_yield = serializers.FloatField(source='asset.twelve_m_yield')
    p_vpa = serializers.FloatField(source='asset.p_vpa')

    class Meta:
        model = models.PortfolioInvestment
        fields = (
            'id',
            'ticker',
            'shares_amount',
            'asset_price_brl',
            'asset_price_usd',
            'share_average_price_brl',
            'share_average_price_usd',
            'total_cost_brl',
            'total_cost_usd',
            'total_today_brl',
            'total_today_usd',
            'category',
            'subcategory',
            'total_profit_brl',
            'total_profit_usd',
            'dividends_profit_brl',
            'dividends_profit_usd',
            'trade_profit_brl',
            'trade_profit_usd',
            'broker',
            'twelve_m_yield',
            'twelve_m_dividend',
            'p_vpa',
            'portfolio_percentage',
            'av_price_minus_div_brl',
            'av_price_minus_div_usd',
            'yield_on_cost_brl',
            'yield_on_cost_usd',
            'profit_without_div_trade_brl',
            'profit_without_div_trade_usd',
            'profit_with_div_trade_brl',
            'profit_with_div_trade_usd',

        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class PortfolioTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PortfolioTrade
        fields = (
            'order',
            'date',
            'portfolio',
            'asset',
            'broker',
            'shares_amount',
            'share_cost_brl',
        )


class PortfolioHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PortfolioHistory
        fields = (
            'date',
            'portfolio',
            'total_today_brl',
            'order_value',
            'tokens_amount',
            'token_price',
        )


class PortfolioDividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PortfolioDividend
        fields = (
            'id', 'ticker', 'category', 'subcategory', 'record_date', 'pay_date', 'shares_amount', 'value_per_share_usd',
            'value_per_share_brl', 'total_dividend_brl', 'total_dividend_usd', 'average_price_usd', 'average_price_brl', 'yield_on_cost',
            'usd_on_pay_date', 'pay_date_by_month_year', 'pay_date_by_year',
        )
