from django.contrib import admin
from .models import Contract  # Importando de models/__init__.py

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'blockchain', 'is_active')
    search_fields = ('name', 'address')
