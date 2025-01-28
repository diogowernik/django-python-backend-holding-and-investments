from django.core.management.base import BaseCommand
from django.db.models import Q
from movies.models import Movie

class Command(BaseCommand):
    help = "Atualiza o campo 'year' com base nos últimos 4 caracteres do título (em lotes)."

    # Tamanho do lote que vamos processar a cada vez
    BATCH_SIZE = 1000

    def handle(self, *args, **options):
        """
        Vamos iterar sobre o queryset em ordem de ID, pegando lotes de BATCH_SIZE.
        Em cada lote, transformamos o year e usamos bulk_update para atualizar tudo de uma só vez.
        """
        updated_count = 0
        last_id = 0

        while True:
            # Carrega até BATCH_SIZE registros cuja PK seja maior que last_id,
            # para evitar pegar sempre os mesmos registros em cada loop
            queryset = (
                Movie.objects
                     .filter(id__gt=last_id)
                     .order_by('id')[:self.BATCH_SIZE]
            )

            if not queryset:
                # Se não vier mais nenhum registro, paramos
                break

            movies_to_update = []
            last_item_id = 0

            for movie in queryset:
                last_item_id = movie.id  # Garante que avancemos no loop a cada registro

                if movie.title and len(movie.title) >= 4:
                    year_str = movie.title[-4:]
                    if year_str.isdigit():
                        new_year = int(year_str)
                        # Verifica se precisamos realmente atualizar
                        if movie.year != new_year:
                            movie.year = new_year
                            movies_to_update.append(movie)

            # Fazemos um bulk_update de todos os filmes deste lote que mudaram
            if movies_to_update:
                Movie.objects.bulk_update(movies_to_update, ['year'])
                updated_count += len(movies_to_update)

            # Atualizamos o `last_id` para continuar do ponto onde paramos
            last_id = last_item_id

        self.stdout.write(
            self.style.SUCCESS(
                f"Processo concluído: 'year' atualizado para {updated_count} filmes."
            )
        )
