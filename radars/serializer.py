from rest_framework import serializers

from arquivo.holding_backend.core.models import Portfolio
from . import models

class RadarItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RadarItem
        fields = ('id', 'name', 'portfolio', 'radar')
        #, 'description', 'price', 'image', 'is_available', 'place', 'category')

class RadarSerializer(serializers.ModelSerializer):
    radar_items = RadarItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'radar_items', 'portfolio')
