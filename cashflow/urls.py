from django.urls import path
from . import views

urlpatterns = [
    path('currency_transactions/', views.CurrencyTransactionList.as_view(), name='currency-transaction-list'),
    path('currency_transactions/<pk>', views.CurrencyTransactionDetail.as_view(), name='currency-transaction-detail'),
]
