# equity/urls.py

from django.urls import path
from .views import ValuationEventList, ValuationEventDetail

urlpatterns = [
    path('valuations/', ValuationEventList.as_view(), name='valuationevent-list'),
    path('valuations/<int:pk>/', ValuationEventDetail.as_view(), name='valuationevent-detail'),
]
