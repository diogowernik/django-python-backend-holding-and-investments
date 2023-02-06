from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from . import permissions, serializers
from . import models
from rest_framework.response import Response
from investments.models import Category, Asset, Fii


# Create your views here.

# Minha Holding

class PortfolioList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.Portfolio.objects.filter(owner_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PortfolioDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioDetailSerializer
    queryset = models.Portfolio.objects.all()
    permission_classes = (IsAuthenticated, )


class PortfolioInvestmentList(generics.ListAPIView):
    # """Handles creating, reading and updating portfolios"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, )
    serializer_class = serializers.PortfolioInvestmentSerializer

    def get_queryset(self):
        return models.PortfolioInvestment.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).select_related(
            'asset__subcategory',
        )


class PortfolioInvestmentDetail(generics.RetrieveUpdateDestroyAPIView):
    """Handles creating, reading and updating portfolios"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioInvestmentSerializer
    queryset = models.PortfolioInvestment.objects.all()
    permission_classes = (IsAuthenticated, )


# class PortfolioHistoryList(generics.ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     serializer_class = serializers.PortfolioHistorySerializer
#     permission_classes = (IsAuthenticated, )

#     def get_queryset(self):
#         return models.PortfolioHistory.objects.filter(
#             portfolio_id=self.kwargs['pk'],
#         )


class CategoryList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Category.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(CategoryList, self).list(request, *args, **kwargs)

        return response


class PortfolioTradeList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioTradeSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.PortfolioTrade.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class PortfolioDividendList(generics.ListAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, )
    serializer_class = serializers.PortfolioDividendSerializer

    def get_queryset(self):
        return models.PortfolioDividend.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).order_by('-pay_date')


class PortfolioEvolutionList(generics.ListAPIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated, )
    serializer_class = serializers.PortfolioEvolutionSerializer

    def get_queryset(self):
        return models.PortfolioEvolution.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).order_by('date')
