from django.urls import path
from . import views

urlpatterns = [
    path('', views.PortfolioList.as_view(), name='portfolio-list'),
    path('<pk>/', views.PortfolioDetail.as_view(), name='portfolio-detail'),
    path('<pk>/assets', views.PortfolioInvestmentList.as_view(), name='portfolio-investment-list'),
    path('<pk>/categories', views.CategoryList.as_view(), name='category-list'),
    path('<pk>/dividends', views.PortfolioDividendList.as_view(), name='portfolio-dividend-list'),
    path('<pk>/evolution', views.PortfolioEvolutionList.as_view(), name='portfolio-evolution-list'),
    path('assets/<pk>/', views.PortfolioInvestmentDetail.as_view(), name='portfolio-investment-detail'),
    path('add-portfolio-asset', views.PortfolioInvestmentCreateView.as_view(), name='portfolio-investment-create'),
    path('<pk>/valuations/', views.ValuationEventList.as_view(), name='valuationevent-list'),
    path('valuations/<int:pk>/', views.ValuationEventDetail.as_view(), name='valuationevent-detail'),
]
