from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

class RadarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'portfolio', 'portfolio_total_value')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['portfolio']
    list_filter = (('portfolio', RelatedFieldListFilter),)
    search_fields = ['name']

class RadarCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'radar', 
        'category', 
        'ideal_category_percentage', 
        'category_percentage_on_portfolio', 
        'category_total_value', 
        'delta_ideal_actual_percentage'
        )
    list_editable = ['ideal_category_percentage']

class RadarAssetAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'radar', 
        'asset', 
        'ideal_asset_percentage_on_category',
        'ideal_asset_percentage_on_portfolio',
        'portfolio_investment_total_value',
        'portfolio_investment_percentage_on_category',
        'portfolio_investment_percentage_on_portfolio',
        'delta_ideal_actual_percentage_on_category',
        'delta_ideal_actual_percentage_on_portfolio',
    )
    list_filter = (('radar', RelatedFieldListFilter),)
    search_fields = ['asset__ticker']

admin.site.register(models.Radar, RadarAdmin)
admin.site.register(models.RadarCategory, RadarCategoryAdmin)
admin.site.register(models.RadarAsset, RadarAssetAdmin)

