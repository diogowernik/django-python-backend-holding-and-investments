from rest_framework import serializers
from .models import KidProfile, PortfolioInvestment, PortfolioDividend

class PortfolioInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioInvestment
        fields = '__all__'

class PortfolioDividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioDividend
        fields = '__all__'

class KidProfileSerializer(serializers.ModelSerializer):
    portfolio_investments = serializers.SerializerMethodField()

    class Meta:
        model = KidProfile
        fields = ['name', 'age', 'portfolio_investments', ...]  # inclua outros campos conforme necessário

    def get_portfolio_investments(self, obj):
        investments = PortfolioInvestment.objects.filter(portfolio=obj.belongs_to)
        return PortfolioInvestmentSerializer(investments, many=True).data
    
    def get_portfolio_dividends(self, obj):
        dividends = PortfolioDividend.objects.filter(portfolio=obj.belongs_to)
        return PortfolioDividendSerializer(dividends, many=True).data
