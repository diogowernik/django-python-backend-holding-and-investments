from django.shortcuts import render
from rest_framework import generics
from . import serializers
from . import models
from rest_framework.response import Response

# Create your views here.


class AssetList(generics.ListAPIView):
    serializer_class = serializers.AssetSerializer

    def get_queryset(self):
        return models.Asset.objects.all()


class FiiList(generics.ListAPIView):
    serializer_class = serializers.FiiSerializer

    def get_queryset(self):
        return models.Fii.objects.all()


class BrStocksList(generics.ListAPIView):
    serializer_class = serializers.BrStocksSerializer

    def get_queryset(self):
        return models.BrStocks.objects.all()
