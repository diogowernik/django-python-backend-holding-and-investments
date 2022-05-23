from rest_framework import serializers
from . import models


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('id', 'ticker', 'slug', 'price')


class FiiSerializer(serializers.ModelSerializer):
    setor_fii = serializers.CharField(source='setor_fii.name')

    class Meta:
        model = models.Fii
        fields = (
            'id',
            'ticker',
            'slug',
            'price',
            'setor_fii',
            'last_dividend',
            'last_yield',
            'six_m_yield',
            'twelve_m_yield',
            'p_vpa'
        )
