from rest_framework import serializers
from . import models
from radars.serializers import RadarSerializer

# Minha Holding

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image')

class PortfolioDetailSerializer(serializers.ModelSerializer):    
    radars = RadarSerializer(many=True, read_only=True)

    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image', 'radars')