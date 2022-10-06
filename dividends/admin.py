from django.contrib import admin
from . import models

# Register your models here.


class DividendAdmin(admin.ModelAdmin):
    list_display = ('asset', 'value_per_share_usd', 'group',
                    'value_per_share_brl', 'record_date', 'pay_date')
    list_editable = ('value_per_share_usd', 'group',
                     'value_per_share_brl', 'record_date', 'pay_date')
    list_filter = ('record_date', 'pay_date')

    # search_fields = ('asset__ticker', 'asset__name')


admin.site.register(models.Dividend, DividendAdmin)
