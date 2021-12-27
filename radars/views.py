from rest_framework import generics
from . import models, serializers #, permissions

# Create your views here.

class RadarList(generics.CreateAPIView):
    # permission_classes = [permissions.PlaceOwnerOrReadOnly]
    serializer_class = serializers.RadarSerializer

class RadarDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    # permission_classes = [permissions.PlaceOwnerOrReadOnly]
    serializer_class = serializers.RadarSerializer
    queryset = models.Radar.objects.all()

class RadarItemList(generics.CreateAPIView):
    # permission_classes = [permissions.PlaceOwnerOrReadOnly]
    serializer_class = serializers.RadarItemSerializer

class RadarItemDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    # permission_classes = [permissions.PlaceOwnerOrReadOnly]
    serializer_class = serializers.RadarItemSerializer
    queryset = models.RadarItem.objects.all()
