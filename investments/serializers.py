from rest_framework import serializers
from . import models

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('id', 'ticker', 'slug', 'price')
        