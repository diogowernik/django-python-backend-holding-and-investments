from rest_framework import serializers
from .models import KidProfile, PortfolioInvestment, PortfolioDividend, KidsQuest, KidsEarns, KidsExpenses, KidsButtons

class PortfolioInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioInvestment
        fields = '__all__'

class PortfolioDividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioDividend
        fields = '__all__'

class KidProfileSerializer(serializers.ModelSerializer):
    # portfolio_investments = serializers.SerializerMethodField()
    # portfolio_dividends = serializers.SerializerMethodField()

    class Meta:
        model = KidProfile
        fields = [
            'name', 
            'slug', 
            'age', 
            'image', 
            'description', 
            'current_balance',
            # 'portfolio_investments', 
            # 'portfolio_dividends',
            ]

    # def get_portfolio_investments(self, obj):
    #     investments = PortfolioInvestment.objects.filter(portfolio=obj.belongs_to)
    #     return PortfolioInvestmentSerializer(investments, many=True).data
    
    # def get_portfolio_dividends(self, obj):
    #     dividends = PortfolioDividend.objects.filter(portfolio=obj.belongs_to)
    #     return PortfolioDividendSerializer(dividends, many=True).data
    

class KidsQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = KidsQuest
        fields = '__all__'


class KidsProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KidProfile
        fields = '__all__'

class KidsEarnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KidsEarns
        fields = '__all__'

class KidsExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KidsExpenses
        fields = '__all__'

class KidsButtonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KidsButtons
        fields = ['belongs_to', 'show_dividends', 'show_quests', 'show_earnings', 'show_expenses', 'show_games', 'show_events', 'show_goals', 'show_education', 'show_growth', 'show_banks', 'show_explore']
