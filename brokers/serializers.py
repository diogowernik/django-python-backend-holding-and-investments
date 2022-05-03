from rest_framework import serializers
from . import models

class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Broker
        fields = ('id', 'name', 'slug')