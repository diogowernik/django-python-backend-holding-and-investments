from django.contrib import admin
from django.urls import path, include

from portfolios import views as portfolio_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('api/portfolios/', portfolio_views.PortfolioList.as_view()),
    path('api/portfolios/<pk>', portfolio_views.PortfolioDetail.as_view()),

]

