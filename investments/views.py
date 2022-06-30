from django.shortcuts import render
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import serializers
from . import models
from rest_framework.response import Response

# Create your views here.


class AssetList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AssetSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.Asset.objects.all()


class FiiList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.FiiSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.Fii.objects.all()


class BrStocksList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.BrStocksSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.BrStocks.objects.all()
