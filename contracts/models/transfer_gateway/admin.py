from django.contrib import admin
from .models import TransferBase, TransferNative, TransferToken

@admin.register(TransferBase)
class TransferBaseAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'status', 'timestamp')
    search_fields = ('sender__address', 'recipient__address')
    readonly_fields = ('timestamp',)

@admin.register(TransferNative)
class TransferNativeAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'native', 'status')
    search_fields = ('sender__address', 'recipient__address', 'native__symbol')

@admin.register(TransferToken)
class TransferTokenAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'token', 'is_allowed', 'status')
    search_fields = ('sender__address', 'recipient__address', 'token__name')
