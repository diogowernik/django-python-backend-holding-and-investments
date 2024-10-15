from rest_framework import serializers
from . import models
from investments.models import Category

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        exclude = ('owner', )  # Exclui 'owner' da validação direta

    def create(self, validated_data):
        # Aqui você pode adicionar o 'owner' se necessário,
        # mas como você já está tratando isso na view, pode não ser necessário.
        return models.Portfolio.objects.create(**validated_data)

class PortfolioDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        fields = "__all__"

class PortfolioInvestmentSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='asset.category.name')
    subcategory = serializers.CharField(source='asset.subcategory.name')
    broker = serializers.CharField(source='broker.name')
    geolocation = serializers.CharField(source='asset.geolocation.name')
    asset_price_brl = serializers.FloatField(source='asset.price_brl')
    asset_price_usd = serializers.FloatField(source='asset.price_usd')


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
            'portfolio_percentage',
            'av_price_minus_div_brl',
            'av_price_minus_div_usd',
            'yield_on_cost_brl',
            'yield_on_cost_usd',
            'profit_without_div_trade_brl',
            'profit_without_div_trade_usd',
            'profit_with_div_trade_brl',
            'profit_with_div_trade_usd',
            'geolocation',

        )

class CreatePortfolioInvestmentSerializer(serializers.ModelSerializer):
    broker_name = serializers.CharField(source='broker.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    asset_ticker = serializers.CharField(source='asset.ticker', read_only=True)
    

    class Meta:
        model = models.PortfolioInvestment
        fields = (
            'id',
            'portfolio',
            'asset',
            'broker',
            'shares_amount',
            'share_average_price_brl',
            'share_average_price_usd',
            'broker_name',
            'asset_ticker',
            'category_name',
            'total_today_brl',
            'total_today_usd',
        )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class PortfolioDividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PortfolioDividend
        fields = (
            'id',
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
            'yield_on_cost_brl',
            'yield_on_cost_usd',
            'usd_on_pay_date',
            'pay_date_by_month_year',
            'pay_date_by_year',
        )

class PortfolioEvolutionSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')

    class Meta:
        model = models.PortfolioEvolution
        fields = (
            'id',
            'category',
            'category_total_brl',
            'category_total_usd',
            'date',
            'evolution_by_year',
        )
