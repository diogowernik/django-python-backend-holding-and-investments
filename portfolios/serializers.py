from rest_framework import serializers
from . import models
from investments.models import Category

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
