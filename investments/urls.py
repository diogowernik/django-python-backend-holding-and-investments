from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.AssetList.as_view(), name='asset-list'),
    path('fiis/', views.FiiList.as_view(), name='fii-list'),
    path('br_stocks/', views.BrStocksList.as_view(), name='br-stocks-list'),
    path('reits/', views.ReitsList.as_view(), name='reits-list'),
    path('stocks/', views.StocksList.as_view(), name='stocks-list'),
]
