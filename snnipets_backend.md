# create env python

python3 -m venv backend_env
source backend_env/bin/activate

# install django
pip install django==3.0.2

python -m pip install -r requirements.txt

/Users/Diogo/WebDevelopment/Projetos/minhaholding/backend_env/bin/python3 -m pip install --upgrade pip

# start server

python manage.py runserver
python manage.py makemigrations
python manage.py migrate

# create superuser

python manage.py createsuperuser

# create fixtures

python manage.py dumpdata --indent 4 > fixtures.json
python manage.py loaddata fixtures.json

# create app with django

python manage.py startapp <app_name>

# install pandas

    pip install pandas

# install sqlalchemy

    pip install sqlalchemy

# install openyxl

    pip install openpyxl
