from django.contrib.admin import SimpleListFilter
from options.models import Call, Put

class CallAssetTickerFilter(SimpleListFilter):
    title = 'asset ticker'
    parameter_name = 'asset__ticker'

    def lookups(self, request, model_admin):
        # Obtém os tickers dos ativos que possuem Calls
        tickers = Call.objects.values_list('asset__ticker', flat=True).distinct()
        return [(ticker, ticker) for ticker in tickers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(asset__ticker=self.value())
        return queryset

class PutAssetTickerFilter(SimpleListFilter):
    title = 'asset ticker'
    parameter_name = 'asset__ticker'

    def lookups(self, request, model_admin):
        # Obtém os tickers dos ativos que possuem Puts
        tickers = Put.objects.values_list('asset__ticker', flat=True).distinct()
        return [(ticker, ticker) for ticker in tickers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(asset__ticker=self.value())
        return queryset
