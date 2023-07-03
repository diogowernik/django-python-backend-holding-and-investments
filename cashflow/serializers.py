from rest_framework import serializers
# from .models import CurrencyTransaction, PortfolioInvestment, CurrencyHolding
from portfolios.models import PortfolioInvestment
from cashflow.models import CurrencyTransaction
from investments.models import CurrencyHolding

class CurrencyTransactionSerializer(serializers.ModelSerializer):
    portfolio_investment = serializers.PrimaryKeyRelatedField(
        queryset=PortfolioInvestment.objects.filter(asset__in=CurrencyHolding.objects.all())
    )

    class Meta:
        model = CurrencyTransaction
        fields = "__all__"
