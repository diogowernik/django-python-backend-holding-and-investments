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


class PortfolioAssetSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='asset.category.name')
    broker = serializers.CharField(source='broker.name')
    setor_fii = serializers.CharField(source='asset.fii.setor_fii')

    class Meta:
        model = models.PortfolioAsset
        fields = (
            'id',
            'ticker',
            'shares_amount',
            'share_average_price_brl',
            'total_cost_brl',
            'total_today_brl',
            'category',
            'profit',
            'dividends_profit',
            'trade_profit',
            'broker',
            'setor_fii',
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = (
            'order',
            'date',
            'portfolio',
            'asset',
            'broker',
            'shares_amount',
            'share_cost_brl',
        )


class PortfolioTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PortfolioToken
        fields = (
            'date',
            'portfolio',
            'total_today_brl',
            'order_value',
            'tokens_amount',
            'token_price',
        )
