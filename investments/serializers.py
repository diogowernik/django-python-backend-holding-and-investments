from rest_framework import serializers
from . import models


class AssetSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.Asset
        fields = (
            'category',
            'subcategory',
            'ticker',
            'slug',
            'dividend_frequency',
            'twelve_m_dividend',
            'p_vpa',
            'top_52w',
            'bottom_52w',
            'twelve_m_yield',
            'price_brl',
            'price_usd',
            'id',
            'percentage_top_52w',
            'percentage_bottom_52w',
            'is_radar',
            'ranking',
            'ideal_percentage',
        )


class FiiSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.Fii
        fields = (
            'id',
            'ticker',
            'slug',
            'price_brl',
            'price_usd',
            'subcategory',
            'twelve_m_yield',
            'ffo_yield',
            'market_cap',
            'liquidity',
            'assets',
            'price_m2',
            'rent_m2',
            'cap_rate',
            'vacancy',
            'p_vpa',
            'ranking',
            'percentage_top_52w',
            'percentage_bottom_52w',
            'is_radar',
            'ranking',
            'is_leveraged',
            'leverage_percentage',
            'ideal_percentage',
        )


class BrStocksSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.BrStocks
        fields = (
            'id',
            'ticker',
            'slug',
            'price_brl',
            'price_usd',
            'subcategory',
            'twelve_m_yield',
            'ev_ebit',
            'roic',
            'roe',
            'pl',
            'p_vpa',
            'ranking',
            'is_radar',
            'percentage_top_52w',
            'percentage_bottom_52w',
        )
    
    # reits and stocks

class ReitsSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.Reit
        fields = (
            'id',
            'ticker',
            'slug',
            'price_brl',
            'price_usd',
            'subcategory',
            'twelve_m_yield',
            'ranking',
            'is_radar',
            'percentage_top_52w',
            'percentage_bottom_52w',
            'der',
            'ffo',
            'p_ffo',
            'p_vpa',
            'roic',
            'earnings_yield',
            'ffo_yield',
            'ideal_percentage',  
        )

class StocksSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.Stocks
        fields = (
            'id',
            'ticker',
            'slug',
            'price_brl',
            'price_usd',
            'subcategory',
            'twelve_m_yield',
            'ranking',
            'is_radar',
            'percentage_top_52w',
            'percentage_bottom_52w',
            'der',
            'ffo',
            'p_ffo',
            'p_vpa',
            'roic',
            'earnings_yield',
            'ffo_yield',
            'ideal_percentage',  
        )
