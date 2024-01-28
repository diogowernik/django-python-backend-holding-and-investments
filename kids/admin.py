from django.contrib import admin
from kids.models import KidProfile


class KidProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'belongs_to')
    list_editable = ['age']
    list_filter = ['belongs_to']
    search_fields = ['name', 'belongs_to__name']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(KidProfile, KidProfileAdmin)