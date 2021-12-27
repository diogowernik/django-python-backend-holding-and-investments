from rest_framework import serializers
# from portfolios import models as portfolio_models
from . import models as radar_models

class RadarItemSerializer(serializers.ModelSerializer):
    class Meta:
        # portfolio = portfolio_models.Portfolio
        model = radar_models.RadarItem
        fields = ('id', 'name', 'portfolio', 'radar')

class RadarSerializer(serializers.ModelSerializer):
    radar_items = RadarItemSerializer(many=True, read_only=True)

    class Meta:
        model = radar_models.Radar
        fields = ('id', 'name', 'radar_items', 'portfolio')
