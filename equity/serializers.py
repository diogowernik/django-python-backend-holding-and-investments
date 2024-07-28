from rest_framework import serializers
from .models import ValuationEvent

class ValuationEventSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    month_year = serializers.SerializerMethodField()

    class Meta:
        model = ValuationEvent
        fields = [
            'id',
            'event_type',
            'value_brl',
            'value_usd',
            'date',
            'year',
            'month_year',
            'total_brl',
            'total_usd',
            'quota_amount',
            'quota_price_brl',
            'quota_price_usd',
            'percentage_change',
            'portfolio'
        ]

    def get_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')

    def get_year(self, obj):
        return obj.date.strftime('%Y')

    def get_month_year(self, obj):
        return obj.date.strftime('%m/%Y')
