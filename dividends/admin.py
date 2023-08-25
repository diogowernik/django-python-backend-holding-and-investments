from django.contrib import admin
from . import models
from datetime import datetime, time
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.db.models import Q
from investments.models import Asset

class DividendFormBase(forms.ModelForm):
    record_date = forms.DateField(widget=AdminDateWidget)
    pay_date = forms.DateField(widget=AdminDateWidget)

    class Meta:
        fields = '__all__'


class DividendAdminBase(admin.ModelAdmin):
    list_display = ('asset', 'value_per_share_usd', 'value_per_share_brl', 'record_date_date', 'pay_date_date')
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

