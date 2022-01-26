from rest_framework import serializers
from . import models

# Minha Holding

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image')

class PortfolioDetailSerializer(serializers.ModelSerializer):    

    class Meta:
        model = models.Portfolio
        fields = ('id', 'name', 'image')