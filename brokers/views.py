from django.shortcuts import render
from rest_framework import generics
from . import serializers
from . import models
from rest_framework.response import Response

# Create your views here.

class BrokerList(generics.ListAPIView):
    serializer_class = serializers.BrokerSerializer

    def get_queryset(self):
        return models.Broker.objects.all()

