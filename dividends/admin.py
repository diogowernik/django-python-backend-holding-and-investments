from django.contrib import admin
from . import models

# Register your models here.


class DividendAdmin(admin.ModelAdmin):
    list_display = ('asset', 'value_per_share_brl', 'record_date', 'pay_date')


admin.site.register(models.Dividend, DividendAdmin)
