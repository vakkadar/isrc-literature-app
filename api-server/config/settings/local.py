"""
Local development settings — SQLite, no Docker needed.

Usage:
    DJANGO_ENV=local python manage.py runserver
    (or just: python manage.py runserver — local is the default)
"""
from .base import *  # noqa: F401,F403

DEBUG = True
SECRET_KEY = "local-dev-insecure-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
