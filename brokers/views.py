from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import serializers
from . import models

class BrokerList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.BrokerSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.Broker.objects.all()
