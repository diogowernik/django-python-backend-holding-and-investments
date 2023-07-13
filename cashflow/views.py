from django.shortcuts import render
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import CurrencyTransaction
from .serializers import CurrencyTransactionSerializer

class CurrencyTransactionList(generics.ListCreateAPIView):
    serializer_class = CurrencyTransactionSerializer

    def get_queryset(self):
        return CurrencyTransaction.objects.filter(portfolio_id=self.kwargs['pk'])
    
class CurrencyTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CurrencyTransactionSerializer
    queryset = CurrencyTransaction.objects.all()

    