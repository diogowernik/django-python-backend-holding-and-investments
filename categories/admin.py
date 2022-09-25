from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from . import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.SubCategory, SubCategoryAdmin)
admin.site.unregister(User)
admin.site.unregister(Group)
