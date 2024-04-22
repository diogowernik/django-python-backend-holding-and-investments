from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from . import serializers
from rest_framework.response import Response
from radar.models import Radar, RadarCategory, RadarAsset

class RadarList(generics.ListCreateAPIView):
    serializer_class = serializers.RadarSerializer

    def get_queryset(self):
        return Radar.objects.filter(portfolio_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(portfolio_id=self.kwargs['pk'])


class RadarDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = serializers.RadarDetailSerializer
    queryset = Radar.objects.all()

    
class RadarCategoryList(generics.ListAPIView):
    serializer_class = serializers.RadarCategorySerializer

    def get_queryset(self):
        queryset = RadarCategory.objects.filter(radar_id=self.kwargs['pk'])
        return sorted(queryset, key=lambda x: x.delta_ideal_actual_percentage, reverse=True)


class RadarAssetList(generics.ListAPIView):
    serializer_class = serializers.RadarAssetSerializer

    def get_queryset(self):
        queryset = RadarAsset.objects.filter(radar_id=self.kwargs['pk'])
        return sorted(queryset, key=lambda x: x.delta_ideal_actual_percentage_on_portfolio, reverse=True)

class RadarCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RadarCategoryDetailSerializer
    queryset = RadarCategory.objects.all()
    

    