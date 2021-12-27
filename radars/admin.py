from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Radar)
admin.site.register(models.RadarItem)
# class RadarAssetAdmin(admin.ModelAdmin):
#     list_display =('asset', 'radar' )
    
# admin.site.register(models.RadarAsset, RadarAssetAdmin)