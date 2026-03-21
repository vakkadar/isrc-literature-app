"""
Local Docker development settings — Postgres in Docker, DEBUG on.

Usage:
    docker compose up  (DJANGO_ENV=docker is set in docker-compose.yml)
"""
import os
from .base import *  # noqa: F401,F403

DEBUG = True

INSTALLED_APPS = ["django.contrib.postgres"] + INSTALLED_APPS  # noqa: F405
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "docker-dev-insecure-key")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "isrc_literature"),
        "USER": os.environ.get("POSTGRES_USER", "isrc_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
