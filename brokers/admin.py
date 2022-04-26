from django.contrib import admin
from . import models

# Register your models here.


class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


admin.site.register(models.Broker, BrokerAdmin)
