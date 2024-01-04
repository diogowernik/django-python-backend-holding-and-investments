import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
import pandas as pd
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Carregar variáveis do arquivo .env
        load_dotenv()

        # Agora, você pode acessar as variáveis usando os.environ.get
        username = os.environ.get('DB_USERNAME')
        password = os.environ.get('DB_PASSWORD')
        host = os.environ.get('DB_HOST')
        port = os.environ.get('DB_PORT', '5432')
        dbname = os.environ.get('DB_NAME')

        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"

        try:
            with create_engine(connection_string).connect() as conn:
                query = "SELECT * FROM publications"
                df = pd.read_sql_query(query, conn)

                    # t.integer  "profile_id"
                    # t.integer  "user_id"
                    # t.string   "title"
                    # t.text     "description"
                    # t.string   "image"
                    # t.string   "slug",                 limit: 255


                # Selecionar apenas colunas específicas
                df = df[['id', 'profile_id', 'user_id', 'title', 'description', 'image', 'slug']]

                # Ordenar os dados pelo 'id'
                df = df.sort_values(by='id')

                # Mostrar as primeiras linhas do DataFrame
                print(df)

                # # create users
                # for index, row in df.iterrows():
                #     # Verificar se o usuário já existe (opcional)
                #     if not User.objects.filter(username=row['username']).exists():
                #         # Criar um novo usuário
                #         user = User.objects.create_user(
                #             id=row['id'],
                #             username=row['username'],  # ou qualquer outro campo que você use como username
                #             email=row['email'],
                #             # Definir outros campos conforme necessário
                #         )
                #         user.set_password('YogaBrasilia04012024$$')  # Defina uma senha padrão ou migre a senha antiga
                #         user.save()


        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        # print("Migration finished!")
