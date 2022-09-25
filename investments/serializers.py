from rest_framework import serializers
from . import models


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('id', 'ticker', 'slug', 'price')


class FiiSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name')

    class Meta:
        model = models.Fii
        fields = (
            'id',
            'ticker',
            'slug',
            'price',
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
            'price',
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
