from django.contrib import admin
from . import models
from datetime import datetime, time
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.db.models import Q
from investments.models import Asset
from django.utils.translation import gettext_lazy as _
from .models import Dividend, Asset  # Importe seus modelos aqui


class DividendFormBase(forms.ModelForm):
    record_date = forms.DateField(widget=AdminDateWidget)
    pay_date = forms.DateField(widget=AdminDateWidget)

    class Meta:
        fields = '__all__'

class DividendAdminBase(admin.ModelAdmin):
    list_display = (
        'pay_date_date',
        'asset', 
        'value_per_share_usd', 
        'value_per_share_brl',
        'record_date_date',
        )
    list_filter = ('record_date', 'pay_date')
    search_fields = ('asset__ticker',)

    def record_date_date(self, obj):
        return obj.record_date.strftime('%d/%m/%Y')

    def pay_date_date(self, obj):
        return obj.pay_date.strftime('%d/%m/%Y')

    def save_model(self, request, obj, form, change):
        obj.record_date = datetime.combine(obj.record_date, time(8))
        obj.pay_date = datetime.combine(obj.pay_date, time(8))
        super().save_model(request, obj, form, change)

class DividendBrForm(DividendFormBase):
    def __init__(self, *args, **kwargs):
        super(DividendBrForm, self).__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(
            Q(privateasset__isnull=False) | Q(brstocks__isnull=False) | Q(fii__isnull=False)
        )

    class Meta(DividendFormBase.Meta):
        model = models.DividendBr
        labels = {
            'asset': 'Ativo',
            'value_per_share_brl': 'Valor por cota R$',
            'record_date': 'Data Com',
            'pay_date': 'Data de Pagamento',
        }
        help_texts = {
                'value_per_share_brl': 'Esta operação gera:<br>'
                            '- PortfolioDividend (Para cada Portfolio que tiver cotas do ativo),<br>'
                            '- DividendReceive,<br>'
                            '- CurrencyTransaction,<br>'
                            '- Conversão de moeda para criar um valor por cota em USD.',
        }

class DividendBrAdmin(DividendAdminBase):
    exclude = ('value_per_share_usd',)
    form = DividendBrForm
admin.site.register(models.DividendBr, DividendBrAdmin)


class DividendUsForm(DividendFormBase):

    def __init__(self, *args, **kwargs):
        super(DividendUsForm, self).__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(
            Q(reit__isnull=False) | Q(stocks__isnull=False)
        )

    class Meta(DividendFormBase.Meta):
        model = models.DividendUs
        labels = {
            'asset': 'Ativo',
            'value_per_share_usd': 'Valor por cota U$',
            'record_date': 'Data Com',
            'pay_date': 'Data de Pagamento',
        }
        help_texts = {
                'value_per_share_usd': 'Esta operação gera:<br>'
                            '- PortfolioDividend (Para cada Portfolio que tiver ações do ativo),<br>'
                            '- DividendReceive,<br>'
                            '- CurrencyTransaction,<br>'
                            '- Conversão de moeda para criar um valor por cota em BRL.',
        }


class DividendUsAdmin(DividendAdminBase):
    exclude = ('value_per_share_brl',)
    form = DividendUsForm
admin.site.register(models.DividendUs, DividendUsAdmin)

class HasDividendListFilter(admin.SimpleListFilter):
    title = _('asset with dividend')
    parameter_name = 'asset_with_dividend'

    def lookups(self, request, model_admin):
        # Retorna uma lista de tuplas com ativos que têm dividendos
        assets_with_dividend = Dividend.objects.values_list('asset', flat=True).distinct()
        return Asset.objects.filter(id__in=assets_with_dividend).values_list('id', 'ticker')

    def queryset(self, request, queryset):
        if self.value():
            # Filtra o queryset por ativos que têm dividendos
            return queryset.filter(asset__id__exact=self.value())
        return queryset

class DividendAdmin(admin.ModelAdmin):
    list_display = (
        'pay_date',
        'asset', 
        'value_per_share_usd', 
        'value_per_share_brl',
        'record_date',
    )
    list_filter = (
        HasDividendListFilter,  # Usando o filtro personalizado
    )
    search_fields = ('asset__ticker',)

    # def record_date_date(self, obj):
    #     return obj.record_date.strftime('%d/%m/%Y')

    # def pay_date_date(self, obj):
    #     return obj.pay_date.strftime('%d/%m/%Y')
admin.site.register(models.Dividend, DividendAdmin)