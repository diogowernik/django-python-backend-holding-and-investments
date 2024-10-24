from django.contrib import admin
from kids.models import KidProfile, KidsQuest, KidsEarns, KidsExpenses, KidsButtons


class KidProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'age', 'belongs_to', 'currency', 'language')
    list_editable = ['age', 'belongs_to', 'currency', 'language']
    list_filter = ['belongs_to']
    search_fields = ['name', 'belongs_to__name']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(KidProfile, KidProfileAdmin)

class KidsQuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'belongs_to', 'is_active')
    list_editable = ['is_active']
    list_filter = ['belongs_to']
    search_fields = ['title', 'belongs_to__name']
    prepopulated_fields = {'quest_key': ('title',)}

admin.site.register(KidsQuest, KidsQuestAdmin)

class KidsEarnsAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'belongs_to')
    list_filter = ['belongs_to']
    list_editable = ['description']
    search_fields = ['description', 'belongs_to__name']

admin.site.register(KidsEarns, KidsEarnsAdmin)

class KidsExpensesAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'belongs_to')
    list_filter = ['belongs_to']
    search_fields = ['description', 'belongs_to__name']

admin.site.register(KidsExpenses, KidsExpensesAdmin)

class KidsButtonsAdmin(admin.ModelAdmin):
    list_display = ('belongs_to',)

admin.site.register(KidsButtons, KidsButtonsAdmin)
