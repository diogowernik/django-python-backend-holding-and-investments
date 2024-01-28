from django.contrib import admin
from kids.models import KidProfile, KidsQuest


class KidProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'belongs_to')
    list_editable = ['age']
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