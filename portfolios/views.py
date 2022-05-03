from rest_framework import generics
from . import permissions, serializers
from . import models
from rest_framework.response import Response
from investments.models import Category


# Create your views here.

# Minha Holding

class PortfolioList(generics.ListCreateAPIView):
    serializer_class = serializers.PortfolioSerializer

    def get_queryset(self):
        return models.Portfolio.objects.filter(owner_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PortfolioDetail(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsOwnerOrReadOnly]
    serializer_class = serializers.PortfolioDetailSerializer
    queryset = models.Portfolio.objects.all()


class PortfolioAssetList(generics.ListAPIView):
    serializer_class = serializers.PortfolioAssetSerializer

    def get_queryset(self):
        return models.PortfolioAsset.objects.all()


class CategoryList(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return Category.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(CategoryList, self).list(request, *args, **kwargs)

        return response


class TransactionList(generics.ListCreateAPIView):
    serializer_class = serializers.TransactionSerializer

    def get_queryset(self):
        return models.Transaction.objects.all()

    def perform_create(self, serializer):
        serializer.save()
