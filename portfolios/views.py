from rest_framework import generics
from . import permissions, serializers
from . import models

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
