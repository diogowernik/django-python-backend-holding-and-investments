from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner, IsOwnerOrReadOnly  # Importando do common
from . import serializers
from . import models
from investments.models import Category

# PortfolioList, apenas donos podem CRUD
class PortfolioList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return models.Portfolio.objects.filter(owner_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PortfolioDetail, apenas donos podem CRUD
class PortfolioDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioDetailSerializer
    queryset = models.Portfolio.objects.all()
    permission_classes = (IsOwner, )  # Somente o dono pode acessar

# PortfolioInvestmentList, apenas donos podem CRUD
class PortfolioInvestmentList(generics.ListAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsOwner, )  # Somente o dono pode acessar
    serializer_class = serializers.PortfolioInvestmentSerializer

    def get_queryset(self):
        return models.PortfolioInvestment.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).select_related(
            'asset__subcategory',
        )

# PortfolioInvestmentDetail, apenas donos podem CRUD
class PortfolioInvestmentDetail(generics.RetrieveUpdateDestroyAPIView):
    # authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioInvestmentSerializer
    queryset = models.PortfolioInvestment.objects.all()
    # permission_classes = (IsOwner, )  # Somente o dono pode acessar

# CategoryList, todos podem ver, apenas admin podem CRUD
class CategoryList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsOwnerOrReadOnly, )  # Todos podem ler, mas apenas o dono pode escrever

    def get_queryset(self):
        return Category.objects.all()

# Apenas donos podem ver e admin pode CRUD
class PortfolioDividendList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwner, )  # Somente o dono pode acessar
    serializer_class = serializers.PortfolioDividendSerializer

    def get_queryset(self):
        return models.PortfolioDividend.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).order_by('-pay_date')

# Apenas donos podem ver e admin pode CRUD
class PortfolioEvolutionList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwner, )  # Somente o dono pode acessar
    serializer_class = serializers.PortfolioEvolutionSerializer

    def get_queryset(self):
        return models.PortfolioEvolution.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).order_by('date')
