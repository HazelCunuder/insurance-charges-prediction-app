"""
Django settings for InsuranceChargePredictionApp project.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT (CORRIGÉ)
load_dotenv()  # Ajout critique : charge le fichier .env AVANT toute utilisation d'os.getenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-only-use-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# CONFIGURATION AUTHENTIFICATION CRITIQUE (AJOUTÉ)
AUTH_USER_MODEL = 'user.CustomUser'  # DOIT ÊTRE DÉFINI AVANT TOUTE MIGRATION
LOGIN_URL = 'user:login'
LOGIN_REDIRECT_URL = 'predict:dashboard'  # À adapter selon votre structure
LOGOUT_REDIRECT_URL = 'user:login'

# Application definition
INSTALLED_APPS = [
    # Our Apps (ORDRE IMPORTANT : user en premier pour le modèle personnalisé)
    'user',
    'predict',
    'appointment',
    'docs',
    
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'tailwind',
    'theme',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Nécessaire pour l'auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'InsuranceChargePredictionApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'theme' / 'templates'],  # Ajout pour base.html
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

WSGI_APPLICATION = 'InsuranceChargePredictionApp.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Correction : utilisation de Path
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALISATION (CORRIGÉ POUR LE FRANÇAIS)
LANGUAGE_CODE = 'fr-fr'  # Changé de 'en-us' à 'fr-fr'
TIME_ZONE = 'Europe/Paris'  # Changé de 'UTC' à timezone française
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'theme' / 'static_src' / 'src',  # Pour styles.css
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Pour collectstatic en production

# Tailwind configuration
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = os.getenv('NPM_BIN_PATH', '/usr/bin/npm')

# SÉCURITÉ RECOMMANDÉE (AJOUTÉ)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'