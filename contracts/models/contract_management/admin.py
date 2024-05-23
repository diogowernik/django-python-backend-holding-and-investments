# contracts/models/contract_management/admin.py

from django.contrib import admin
from .models import FeeSetting, AllowedToken, ContractStatus

@admin.register(FeeSetting)
class FeeSettingAdmin(admin.ModelAdmin):
    list_display = ('fee_bps', 'max_fee_bps')

@admin.register(AllowedToken)
class AllowedTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'is_allowed')
    list_filter = ('is_allowed',)

@admin.register(ContractStatus)
class ContractStatusAdmin(admin.ModelAdmin):
    list_display = ('contract', 'is_paused', 'last_updated')
    list_filter = ('is_paused',)
    actions = ['toggle_pause']

    def toggle_pause(self, request, queryset):
        for contract_status in queryset:
            contract_status.toggle_pause()
            contract_status.save()
    toggle_pause.short_description = "Toggle the pause status of selected contracts"
