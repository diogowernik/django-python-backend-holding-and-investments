from rest_framework import serializers
from radar.models import Radar, RadarCategory, RadarAsset

class RadarSerializer(serializers.ModelSerializer):
    radar_id = serializers.IntegerField(source='id')
    id = serializers.IntegerField(source='portfolio.id')

    class Meta:
        model = Radar
        fields = (
            'radar_id',
            'id', 
            'name', 
            'slug', 
            'portfolio'
            )

class RadarDetailSerializer(serializers.ModelSerializer):
    radar_id = serializers.IntegerField(source='id')
    id = serializers.IntegerField(source='portfolio.id')

    class Meta:
        model = Radar
        fields = (
            'radar_id',
            'id', 
            'name', 
            'slug', 
            )

class RadarCategorySerializer(serializers.ModelSerializer):
    portfolio_total_value = serializers.FloatField(source='radar.portfolio_total_value', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    radar_id = serializers.IntegerField(source='radar.id', read_only=True)
    id = serializers.IntegerField(source='radar.portfolio.id', read_only=True)
    category_total_value = serializers.SerializerMethodField()
    category_percentage_on_portfolio = serializers.FloatField(read_only=True)
    delta_ideal_actual_percentage = serializers.SerializerMethodField()

    def get_delta_ideal_actual_percentage(self, obj):
        return obj.delta_ideal_actual_percentage

    def get_category_total_value(self, obj):
        return obj.category_total_value

    class Meta:
        model = RadarCategory
        fields = (
            'radar_id',
            'id',
            'portfolio_total_value',
            'radar',
            'category',
            'ideal_category_percentage',
            'category_percentage_on_portfolio',
            'category_total_value',
            'delta_ideal_actual_percentage',
        )


class RadarAssetSerializer(serializers.ModelSerializer):
    portfolio_total_value = serializers.FloatField(source='radar.portfolio_total_value')
    category = serializers.CharField(source='asset.category.name')
    asset = serializers.CharField(source='asset.ticker')
    # category_total_value = serializers.FloatField(source='radar_category.category_total_value')
    category_total_value = serializers.SerializerMethodField()
    radar_id = serializers.IntegerField(source='radar.id')
    id = serializers.IntegerField(source='radar.portfolio.id')
    portfolio = serializers.CharField(source='radar.portfolio.name')
    price_brl = serializers.FloatField(source='asset.price_brl')
    price_usd = serializers.FloatField(source='asset.price_usd')

    delta_ideal_actual_percentage_on_portfolio = serializers.SerializerMethodField()
    delta_ideal_actual_percentage_on_category = serializers.SerializerMethodField()

    def get_category_total_value(self, obj):
        # Verifica se radar_category é None antes de tentar acessar category_total_value
        if obj.radar_category is not None:
            return obj.radar_category.category_total_value
        else:
            return 0

    class Meta:
        model = RadarAsset
        fields = (
            'id',
            'radar_id',
            'asset',
            'portfolio_investment_total_value',

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

            'price_brl',
            'price_usd',
        )

    def get_delta_ideal_actual_percentage_on_portfolio(self, obj):
        return obj.delta_ideal_actual_percentage_on_portfolio

    def get_delta_ideal_actual_percentage_on_category(self, obj):
        return obj.delta_ideal_actual_percentage_on_category
