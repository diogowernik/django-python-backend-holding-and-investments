# movies/models.py
from django.db import models

class Movie(models.Model):
    imdb_id = models.CharField(max_length=50, unique=True)
    tmdb_id = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    embed_url = models.URLField(max_length=500, blank=True, null=True)
    embed_url_tmdb = models.URLField(max_length=500, blank=True, null=True)
    quality = models.CharField(max_length=50, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)  # Novo campo


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.imdb_id})"
