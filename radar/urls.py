from django.urls import path
from . import views

urlpatterns = [
    path('<pk>/radars', views.RadarList.as_view(), name='radar-list'),
    path('radars/<pk>', views.RadarDetail.as_view(), name='radar-detail'),
    path('radars/<pk>/categories', views.RadarCategoryList.as_view(), name='radar-category-list'),
    path('radar_categories/<pk>', views.RadarCategoryDetail.as_view(), name='radar-category-detail'),
    path('radars/<pk>/assets', views.RadarAssetList.as_view(), name='radar-asset-list'),
]
