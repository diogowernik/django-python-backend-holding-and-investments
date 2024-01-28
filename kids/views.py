from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner
from .models import KidProfile, KidsQuest
from portfolios.models import PortfolioInvestment, PortfolioDividend
from .serializers import KidProfileSerializer, PortfolioInvestmentSerializer, PortfolioDividendSerializer, KidsQuestSerializer

class KidProfileDetail(generics.RetrieveAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = KidProfileSerializer
    queryset = KidProfile.objects.all()
    lookup_field = 'slug'  # Adicione isto


class KidPortfolioInvestmentList(generics.ListAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PortfolioInvestmentSerializer

    def get_queryset(self):
        kid_profile = KidProfile.objects.get(slug=self.kwargs['slug'])
        return PortfolioInvestment.objects.filter(portfolio=kid_profile.belongs_to)
    
class KidPortfolioDividendList(generics.ListAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PortfolioDividendSerializer

    def get_queryset(self):
        kid_profile = KidProfile.objects.get(slug=self.kwargs['slug'])
        return PortfolioDividend.objects.filter(portfolio=kid_profile.belongs_to)

class KidsQuestList(generics.ListAPIView):
    serializer_class = KidsQuestSerializer

    def get_queryset(self):
        kid_profile = KidProfile.objects.get(slug=self.kwargs['slug'])
        return KidsQuest.objects.filter(belongs_to=kid_profile, is_active=True)

class KidsQuestDetail(generics.RetrieveAPIView):
    serializer_class = KidsQuestSerializer
    queryset = KidsQuest.objects.all()
    lookup_field = 'quest_key'