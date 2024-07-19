# equity/views.py

from rest_framework import generics
from .models import ValuationEvent
from .serializers import ValuationEventSerializer

class ValuationEventList(generics.ListCreateAPIView):
    serializer_class = ValuationEventSerializer

    def get_queryset(self):
        portfolio_id = self.kwargs['portfolio_id']
        return ValuationEvent.objects.filter(portfolio_id=portfolio_id)

class ValuationEventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ValuationEvent.objects.all()
    serializer_class = ValuationEventSerializer
