from rest_framework import serializers
from radar.models import Radar, RadarCategory, RadarAsset

class RadarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Radar
        fields = ('id', 'name', 'slug')

class RadarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Radar
        fields = ('id', 'name', 'slug', 'portfolio')

class RadarCategorySerializer(serializers.ModelSerializer):
    portfolio = serializers.CharField(source='radar.portfolio.name')
    portfolio_total_value = serializers.FloatField(source='radar.portfolio_total_value')
    category = serializers.CharField(source='category.name')

    class Meta:
        model = RadarCategory
        fields = (
            'id',
            'portfolio',
            'portfolio_total_value',
            'radar',
            'category',
            'ideal_category_percentage',
            'category_percentage_on_portfolio',
            'category_total_value',
            'delta_ideal_actual_percentage',

        )

class RadarAssetSerializer(serializers.ModelSerializer):
    portfolio = serializers.CharField(source='radar.portfolio.name')
    portfolio_total_value = serializers.FloatField(source='radar.portfolio_total_value')
    category = serializers.CharField(source='asset.category.name')
    asset = serializers.CharField(source='asset.ticker')
    category_total_value = serializers.FloatField(source='radar_category.category_total_value')

    class Meta:
        model = RadarAsset
        fields = (
            'id',
            'radar',
            'asset',
            'portfolio_investment_total_value', # portfolio_investment.asset.ticker = asset

            'portfolio',
            'portfolio_total_value',
            'ideal_asset_percentage_on_portfolio',
            'portfolio_investment_percentage_on_portfolio',
            'delta_ideal_actual_percentage_on_portfolio',
            
            'category',
            'category_total_value',
            'ideal_asset_percentage_on_category',
            'portfolio_investment_percentage_on_category',
            'delta_ideal_actual_percentage_on_category',
            
        )
