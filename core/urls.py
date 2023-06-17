from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
from djoser.views import (
    TokenCreateView
)

from portfolios import views as portfolio_views
from brokers import views as broker_views
from investments import views as investment_views
from .views import home


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    # permissions only owner
    # permission_classes=(permissions.IsAuthenticated,),
    # permission_classes=[permissions.AllowAny],
)

# url permission_classes=[permissions.AllowAny]

urlpatterns = [
     re_path(r'^swagger(?P<format>\.json|\.yaml)$',
               schema_view.without_ui(cache_timeout=0), name='schema-json'),
     re_path(r'^swagger/$', schema_view.with_ui('swagger',
               cache_timeout=0), name='schema-swagger-ui'),
     re_path(r'^redoc/$', schema_view.with_ui('redoc',
               cache_timeout=0), name='schema-redoc'),

     path('admin/', admin.site.urls),


     # removed registration
     path('auth/', include('djoser.urls')),
     path('auth/', include('djoser.urls.authtoken')),
     path('auth/token/login/', TokenCreateView.as_view(), name='login'),

     path('api/portfolios/', portfolio_views.PortfolioList.as_view()),
     path('api/trade/', portfolio_views.PortfolioTradeList.as_view()),
     path('api/portfolios/<pk>', portfolio_views.PortfolioDetail.as_view()),
     path('api/portfolios/<pk>/assets',
          portfolio_views.PortfolioInvestmentList.as_view()),
     path('api/portfolios/<pk>/categories',
          portfolio_views.CategoryList.as_view()),
     # path('api/portfolios/<pk>/history',
     #      portfolio_views.PortfolioHistoryList.as_view()),
     path('api/portfolios/<pk>/dividends',
          portfolio_views.PortfolioDividendList.as_view()),
     path('api/portfolio_assets/<pk>',
          portfolio_views.PortfolioInvestmentDetail.as_view()),
     path('api/portfolio/<pk>/evolution',
          portfolio_views.PortfolioEvolutionList.as_view()),
     path('api/brokers/', broker_views.BrokerList.as_view()),
     path('api/assets/', investment_views.AssetList.as_view()),
     path('api/fiis/', investment_views.FiiList.as_view()),
     path('api/br_stocks/', investment_views.BrStocksList.as_view()),
     path('api/reits/', investment_views.ReitsList.as_view()),
     path('api/stocks/', investment_views.StocksList.as_view()),

     url(r'^$', home, name='home'),

]
