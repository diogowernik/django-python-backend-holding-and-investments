from django.contrib import admin
from . import models
# from django.contrib.auth.models import User
# from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticker', 'slug', 'name', 'price_brl', 'price_usd')
    prepopulated_fields = {'slug': ('ticker',)}
    list_editable = ['slug', 'price_brl', 'price_usd']
admin.site.register(models.Currency, CurrencyAdmin)

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
            # cashflow
            app['name'] = app['name'].replace('Cashflow', 'Cashflow')
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
            'Equity': 0,
            'Cashflow': 1,
            'Trade': 2,
            'Portfolios': 3,
            'Radar': 4,
            'Investmentos': 5,
            'Timewarp': 6,
            'Dividendos': 7,
            'Categorias': 8,
            'Corretoras': 9,
            'Autenticação e Autorização': 10,
            'Token de Autenticação': 11,
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

class CustomUserAdmin(UserAdmin):
    list_display = ('id',) + UserAdmin.list_display

# Desregistrar o modelo User padrão do admin
admin.site.unregister(User)

# Registrar novamente com a classe CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.get_app_list = app_resort(admin.site.get_app_list)