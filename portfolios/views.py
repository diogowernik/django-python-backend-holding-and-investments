from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner, IsOwnerOrReadOnly  # Importando do common
from . import serializers
from . import models
from investments.models import Category
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response



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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwner, )  # Somente o dono pode acessar
    serializer_class = serializers.PortfolioInvestmentSerializer

    def get_queryset(self):
        return models.PortfolioInvestment.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).select_related(
            'asset__subcategory',
        )

# PortfolioInvestmentDetail, apenas donos podem CRUD
class PortfolioInvestmentDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
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

class PortfolioInvestmentCreateView(generics.ListCreateAPIView):
    queryset = models.PortfolioInvestment.objects.all()
    serializer_class = serializers.CreatePortfolioInvestmentSerializer

    def perform_create(self, serializer):
        try:
            return serializer.save()  # Modifique para retornar o objeto criado
        except IntegrityError as e:
            if 'unique_together' in str(e):
                return Response({
                    'success': False,
                    'message': 'You already have this asset on this broker, try to update the amount.'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'message': 'An error occurred while saving the investment: {}'.format(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An unexpected error occurred: {}'.format(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        created_investment = self.create(request, *args, **kwargs)
        if created_investment.status_code == 400:
            return created_investment  # Return error response directly
        investment_data = created_investment.data
        investment_data['id'] = created_investment.data['id']  # Ensure 'id' is included
        return Response({
            'success': True,
            'message': 'Investment created successfully',
            'data': investment_data  # Return complete data including 'id'
        }, status=status.HTTP_201_CREATED)
