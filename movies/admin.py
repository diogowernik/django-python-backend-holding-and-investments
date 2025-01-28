from django.contrib import admin

# Register your models here.

# movies/admin.py

from django.contrib import admin
from .models import Movie

@admin.register(Movie)

class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "title", "imdb_id", "tmdb_id", "quality", "created_at", "embed_url", "embed_url_tmdb")
    search_fields = ("title", "imdb_id")
    list_filter = ("quality", "year")
    ordering = ("title",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("imdb_id", "title", "quality", "year", "tmdb_id")
        }),
        ("Embed", {
            "fields": ("embed_url", "embed_url_tmdb")
        }),
        ("Data", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )