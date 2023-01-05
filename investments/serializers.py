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
            'percentage_bottom_52w'
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
            'last_dividend',
            'last_yield',
            'six_m_yield',
            'twelve_m_yield',
            'p_vpa',
            'ranking'
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
            'ranking_all'
        )
