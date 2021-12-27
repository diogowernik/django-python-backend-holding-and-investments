from django.contrib import admin
from django.urls import path, include

from portfolios import views as portfolio_views
from radars import views as radar_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('api/portfolios/', portfolio_views.PortfolioList.as_view()),
    path('api/portfolios/<pk>', portfolio_views.PortfolioDetail.as_view()),

    path('api/radars/', radar_views.RadarList.as_view()),
    path('api/radars/<pk>', radar_views.RadarDetail.as_view()),

    path('api/radar_items/', radar_views.RadarItemList.as_view()),
    path('api/radar_items/<pk>', radar_views.RadarItemDetail.as_view()),

]

