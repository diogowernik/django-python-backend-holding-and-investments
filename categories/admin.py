from django.contrib import admin
# from django.contrib.auth.models import User
# from django.contrib.auth.models import Group
from . import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['slug']

class TagsAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.SubCategory, SubCategoryAdmin)
admin.site.register(models.Tag, TagsAdmin)
# admin.site.unregister(User)
# admin.site.unregister(Group)

# Ordering of the admin site


def app_resort(func):
    def inner(*args, **kwargs):
        app_list = func(*args, **kwargs)
        # Useful to discover your app and module list:
        #import pprint
        # pprint.pprint(app_list)

        # rename the apps names
        for app in app_list:
            app['name'] = app['name'].replace('Investments', 'Investmentos')
            app['name'] = app['name'].replace('Categories', 'Categorias')
            app['name'] = app['name'].replace('Dividends', 'Dividendos')
            app['name'] = app['name'].replace('Brokers', 'Corretoras')
            app['name'] = app['name'].replace(
                'Authentification and Authorization', 'Autenticação e Autorização')
            app['name'] = app['name'].replace(
                'Auth Token', 'Token de Autenticação')

        app_sort_key = 'name'
        app_ordering = {
            'Investmentos': 1,
            'Portfolios': 2,
            'Categorias': 3,
            'Dividendos': 4,
            'Corretoras': 5,
            'Autenticação e Autorização': 6,
            'Token de Autenticação': 7,
        }

        resorted_app_list = sorted(
            app_list, key=lambda x: app_ordering[x[app_sort_key]] if x[app_sort_key] in app_ordering else 1000)

        # model_sort_key = 'object_name'
        # model_ordering = {
        #     "Model1": 1,
        #     "Model2": 2,
        #     "Model3": 3,
        #     "Model14": 4,
        # }
        # for app in resorted_app_list:
        #     app['models'].sort(key=lambda x: model_ordering[x[model_sort_key]] if x[model_sort_key] in model_ordering else 1000)
        return resorted_app_list
    return inner


admin.site.get_app_list = app_resort(admin.site.get_app_list)
