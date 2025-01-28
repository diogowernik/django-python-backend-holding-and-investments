# movies/management/commands/update_latest_movies_from_vidsrc.py
from django.core.management.base import BaseCommand
from movies.models import Movie
import requests

class Command(BaseCommand):
    help = (
        "Busca apenas os filmes mais recentes do vidsrc.xyz (latest) "
        "e para quando encontrar um certo número de filmes repetidos."
    )

    def add_arguments(self, parser):
        # Permite escolher quantas páginas ler e quantos repetidos tolerar
        parser.add_argument(
            '--max-pages',
            type=int,
            default=10,  # ou outro valor razoável
            help='Número máximo de páginas para ler (padrão = 10).'
        )
        parser.add_argument(
            '--repeated-threshold',
            type=int,
            default=3,
            help='Para a importação quando chegar a essa quantidade de filmes repetidos (padrão = 3).'
        )

    def handle(self, *args, **options):
        base_url = "https://vidsrc.xyz/movies/latest/page-"
        max_pages = options['max_pages']
        repeated_threshold = options['repeated_threshold']

        page = 1
        repeated_count = 0

        self.stdout.write(self.style.NOTICE(
            f"Iniciando importação incremental. Tolerância de repetidos: {repeated_threshold}"
        ))

        while page <= max_pages and repeated_count < repeated_threshold:
            url = f"{base_url}{page}.json"
            self.stdout.write(f"Buscando página {page}: {url}")

            resp = requests.get(url)
            if resp.status_code != 200:
                self.stdout.write(self.style.ERROR(
                    f"Erro na página {page} - status code: {resp.status_code}"
                ))
                break

            data = resp.json()
            results = data.get("result", [])

            # Se vier vazio, não há mais filmes nessa página
            if not results:
                self.stdout.write(self.style.WARNING(
                    f"Página {page} vazia ou sem resultados. Encerrando..."
                ))
                break

            for item in results:
                imdb_id = item.get("imdb_id")
                if not imdb_id:
                    # Se não tiver imdb_id, ignora
                    continue

                # Preparamos dados para a criação
                movie_data = {
                    "tmdb_id": item.get("tmdb_id"),
                    "title": item.get("title"),
                    "embed_url": item.get("embed_url"),
                    "embed_url_tmdb": item.get("embed_url_tmdb"),
                    "quality": item.get("quality"),
                }

                # Tenta criar
                movie, created = Movie.objects.get_or_create(
                    imdb_id=imdb_id,
                    defaults=movie_data
                )

                if not created:
                    # Se já existe, incrementa o contador de repetidos
                    repeated_count += 1
                    if repeated_count >= repeated_threshold:
                        self.stdout.write(self.style.WARNING(
                            f"Já encontramos {repeated_count} filmes repetidos. Parando a importação."
                        ))
                        break
                else:
                    # Se quiser, você pode imprimir algo para saber que adicionou um filme novo
                    self.stdout.write(self.style.SUCCESS(
                        f"Novo filme adicionado: {movie.title} ({movie.imdb_id})"
                    ))

            # Se no meio do loop interno já chegamos ao limite de repetidos, saímos
            if repeated_count >= repeated_threshold:
                break

            self.stdout.write(self.style.SUCCESS(f"Página {page} processada."))
            page += 1

        self.stdout.write(self.style.SUCCESS("Importação incremental finalizada."))


# python manage.py update_latest_movies_from_vidsrc --max-pages=5 --repeated-threshold=3
