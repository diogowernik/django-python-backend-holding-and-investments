# core/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
from djoser.views import (TokenCreateView)
from .views import home
from portfolios import views as portfolio_views
from brokers import views as broker_views
from investments import views as investment_views
from radar import views as radar_views
from cashflow import views as cashflow_views
from kids import views as kids_views
from wtree.views import MetaMaskRegisterView, MetaMaskLoginView
from django.conf import settings


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
    permission_classes=(AllowAny,) if settings.DEBUG else (IsAuthenticated,),

)

urlpatterns = [
     re_path(r'^swagger(?P<format>\.json|\.yaml)$',
               schema_view.without_ui(cache_timeout=0), name='schema-json'),
     re_path(r'^swagger/$', schema_view.with_ui('swagger',
               cache_timeout=0), name='schema-swagger-ui'),
     re_path(r'^redoc/$', schema_view.with_ui('redoc',
               cache_timeout=0), name='schema-redoc'),

     path('admin/', admin.site.urls),

     path('auth/', include('djoser.urls')),
     path('auth/', include('djoser.urls.authtoken')),
     # path('auth/token/login/', TokenCreateView.as_view(), name='login'),
     path('auth/metamask/register/', MetaMaskRegisterView.as_view(), name='register_with_metamask'),
     path('auth/metamask/login/', MetaMaskLoginView.as_view(), name='login_with_metamask'),
# 
     path('api/portfolios/', portfolio_views.PortfolioList.as_view()),
     path('api/portfolios/<pk>', portfolio_views.PortfolioDetail.as_view()),
     path('api/portfolios/<pk>/assets',
          portfolio_views.PortfolioInvestmentList.as_view()),
     path('api/portfolios/<pk>/categories',
          portfolio_views.CategoryList.as_view()),
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
     path('api/portfolios/<pk>/radars',
          radar_views.RadarList.as_view()),
     path('api/radars/<pk>', radar_views.RadarDetail.as_view()),
     path('api/radars/<pk>/categories', radar_views.RadarCategoryList.as_view()),
     path('api/radar_categories/<pk>', radar_views.RadarCategoryDetail.as_view()),
     path('api/radars/<pk>/assets', radar_views.RadarAssetList.as_view(), name='radar_category_detail'),
     # cashflow currency transactions
     path('api/portfolios/<pk>/currency_transactions', cashflow_views.CurrencyTransactionList.as_view()),
     path('api/currency_transactions/<pk>', cashflow_views.CurrencyTransactionDetail.as_view()),
     # kids
     path('api/kids/', kids_views.KidProfileList.as_view()),
     path('api/kids/<slug:slug>', kids_views.KidProfileDetail.as_view()),
     path('api/kids/<slug:slug>/quests', kids_views.KidsQuestList.as_view()),
     path('api/kids/<slug:slug>/quests/<quest_key>', kids_views.KidsQuestDetail.as_view()),
     # kids dividends list
     # path('api/kids/<slug:slug>/dividends', kids_views.KidPortfolioDividendList.as_view()), # mudar e usar o PortfolioDividendList
     # kids expenses and earns
     path('api/kids/<slug:slug>/earns', kids_views.KidsEarnsList.as_view()),
     path('api/kids/<slug:slug>/earns/<int:pk>', kids_views.KidsEarnsDetail.as_view()),
     path('api/kids/<slug:slug>/expenses', kids_views.KidsExpensesList.as_view()),
     path('api/kids/<slug:slug>/expenses/<int:pk>', kids_views.KidsExpensesDetail.as_view()),
     # kids buttons
     path('api/kids/<slug:slug>/buttons', kids_views.KidsButtonsDetail.as_view()),

     url(r'^$', home, name='home'),

]
