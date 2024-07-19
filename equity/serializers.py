# equity/serializers.py

from rest_framework import serializers
from .models import ValuationEvent

class ValuationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValuationEvent
        fields = '__all__'
