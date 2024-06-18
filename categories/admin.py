from django.contrib import admin
from . import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']

admin.site.register(models.Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


admin.site.register(models.SubCategory, SubCategoryAdmin)

class GeoLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']

admin.site.register(models.GeoLocation, GeoLocationAdmin)

