from rest_framework import serializers
from .models import PortfolioDividend

class PortfolioDividendSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='asset.ticker', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    pay_date_by_month_year = serializers.SerializerMethodField()
    pay_date_by_year = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioDividend
        fields = [
            'id',
            'ticker',
            'category',
            'record_date',
            'pay_date',
            'shares_amount',
            'value_per_share_brl',
            'value_per_share_usd',
            'average_price_brl',
            'average_price_usd',
            'currency',
            'portfolio_investment',
            'asset',
            'trade_history',
            'dividend',
            'pay_date_by_month_year',
            'pay_date_by_year',
            'total_dividend_brl',
            'total_dividend_usd',
        ]

    def get_pay_date_by_month_year(self, obj):
        return obj.pay_date.strftime('%m/%Y') if obj.pay_date else None

    def get_pay_date_by_year(self, obj):
        return obj.pay_date.strftime('%Y') if obj.pay_date else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.record_date:
            representation['record_date'] = instance.record_date.strftime('%d/%m/%Y')
        if instance.pay_date:
            representation['pay_date'] = instance.pay_date.strftime('%d/%m/%Y')
        return representation
