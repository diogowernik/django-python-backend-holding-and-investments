# create env python

python3 -m venv backend_env
source backend_env/bin/activate
cd backend
python manage.py runserver

source backend_env/bin/activate
cd backend
python manage.py update
python manage.py update_token

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

python manage.py dumpdata --indent 4 --exclude admin.logentry --exclude auth.permission --exclude contenttypes --exclude sessions > fixtures.json

python manage.py loaddata fixtures.json

# clean database django before load fixtures

python manage.py flush

# create app with django

python manage.py startapp <app_name>
- app comum
python manage.py startapp trade
python manage.py startapp timewarp
python manage.py startapp wtree

# install pandas

    pip install pandas

# install sqlalchemy

    pip install sqlalchemy

# install openyxl

    pip install openpyxl

# create app inside django project

    python manage.py startapp cashflow

# update requirements.txt

    pip freeze > requirements.txt
