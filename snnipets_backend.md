# create env python

python3 -m venv backend_env
source backend_env/bin/activate

python3 -m pip install -r requirements.txt

/Users/Diogo/WebDevelopment/Projetos/minhaholding/backend_env/bin/python3 -m pip install --upgrade pip

# start server

python manage.py runserver
python manage.py migrate

# create superuser

python manage.py createsuperuser

# create fixtures

python manage.py dumpdata --indent 4 > fixtures.json
