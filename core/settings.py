from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta do Django
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')

# Configuração de DEBUG baseada no ambiente
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False
}

INSTALLED_APPS = [
    'django_admin_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'investments',
    'portfolios',
    'categories',
    'dividends',
    'brokers',
    'cashflow',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'admin_auto_filters',
    'radar',
    'common',
    'timewarp',
    'trade',
    'equity',
    'kids',
    'wtree',
    'blockchains',
    'contracts',
    'options',
    'admin_commands',
    'movies',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
DATE_FORMAT = (('d/m/Y'))
DATE_INPUT_FORMATS = (('%d/%m/%Y'),)
USE_L10N = False
USE_TZ = False
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DATE_FORMAT': "%d/%m/%Y",
    'DATE_INPUT_FORMATS': [("%d/%m/%Y"),  ("%Y-%m-%d")],
}


ALLOWED_HOSTS = [
    'localhost',
    'api.wtr.ee',
]

react_app_host = os.getenv('REACT_APP_HOST')

CORS_ALLOWED_ORIGINS = [
    'https://wtr.ee',
    'https://kids.wtr.ee',
    'https://holding.wtr.ee',
    'https://movies.wtr.ee',
    'http://localhost:3000',
]
# Apenas admin podem criar contas
# DJOSER = {
#     'PERMISSIONS': {
#         'user_create': ['rest_framework.permissions.IsAdminUser'],
#     },
# }

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
