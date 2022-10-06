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


class PortfolioAssetList(generics.ListAPIView):
    """Handles creating, reading and updating portfolios"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioAssetSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.PortfolioAsset.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).select_related(
            'asset__subcategory',
        )


class PortfolioAssetDetail(generics.RetrieveUpdateDestroyAPIView):
    """Handles creating, reading and updating portfolios"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioAssetSerializer
    queryset = models.PortfolioAsset.objects.all()
    permission_classes = (IsAuthenticated, )


class PortfolioTokenList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioTokenSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.PortfolioToken.objects.filter(
            portfolio_id=self.kwargs['pk'],
        )


class CategoryList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Category.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(CategoryList, self).list(request, *args, **kwargs)

        return response


class TransactionList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.TransactionSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.Transaction.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class PortfolioDividendList(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.PortfolioDividendSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return models.PortfolioDividend.objects.filter(
            portfolio_id=self.kwargs['pk'],
        ).order_by('-pay_date')
