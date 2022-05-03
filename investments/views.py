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