# movies/management/commands/get_movies_from_vidsrc.py
from django.core.management.base import BaseCommand
from movies.models import Movie
import requests

class Command(BaseCommand):
    help = "Importa filmes da API do vidsrc.xyz (latest)."

    def add_arguments(self, parser):
        # Opcional: permitir que o usuário passe um --max-pages
        parser.add_argument(
            '--max-pages',
            type=int,
            default=9999,  # Algum número bem alto para não parar cedo
            help='Número máximo de páginas para ler (default = 9999).'
        )

    def handle(self, *args, **options):
        base_url = "https://vidsrc.xyz/movies/latest/page-"
        max_pages = options['max_pages']

        page = 1
        while page <= max_pages:
            url = f"{base_url}{page}.json"
            self.stdout.write(f"Buscando página {page}: {url}")

            resp = requests.get(url)
            if resp.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"Erro na página {page} - status code: {resp.status_code}")
                )
                break

            data = resp.json()
            results = data.get("result", [])

            if not results:
                # Se 'result' vier vazio, não há mais filmes nessa página
                self.stdout.write(self.style.WARNING(f"Página {page} vazia. Encerrando..."))
                break

            # Processa cada filme
            for item in results:
                imdb_id = item.get("imdb_id")
                if not imdb_id:
                    # Se não tiver imdb_id, pula
                    continue

                movie_data = {
                    "tmdb_id": item.get("tmdb_id"),
                    "title": item.get("title"),
                    "embed_url": item.get("embed_url"),
                    "embed_url_tmdb": item.get("embed_url_tmdb"),
                    "quality": item.get("quality"),
                }

                movie, created = Movie.objects.get_or_create(
                    imdb_id=imdb_id,
                    defaults=movie_data  # Cria com esses valores
                )
                if not created:
                    # Se já existe, você pode optar por atualizar
                    # movie.quality = item.get("quality")
                    # ...
                    # movie.save()
                    pass

            self.stdout.write(self.style.SUCCESS(f"Página {page} importada."))

            page += 1

        self.stdout.write(self.style.SUCCESS("Importação finalizada."))
