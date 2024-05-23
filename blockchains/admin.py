from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Blockchain, Token, Native

@admin.register(Blockchain)
class BlockchainAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_url')
    search_fields = ('name', 'slug')

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'blockchain', 'contract_address', 'decimals', 'slug', 'icon_url')
    list_filter = ('blockchain',)
    search_fields = ('name', 'symbol', 'contract_address')
    raw_id_fields = ('blockchain',)

@admin.register(Native)
class NativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'blockchain', 'slug', 'icon_url')
    list_filter = ('blockchain',)
    search_fields = ('name', 'symbol')
    raw_id_fields = ('blockchain',)
