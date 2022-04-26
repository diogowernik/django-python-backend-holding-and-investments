from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from . import models

# Register your models here.

admin.site.register(models.Category)
admin.site.register(models.SetorFii)
admin.site.register(models.SetorCrypto)
