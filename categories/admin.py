from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


class SetorFiiAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


class SetorCryptoAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.SetorFii, SetorFiiAdmin)
admin.site.register(models.SetorCrypto, SetorCryptoAdmin)
