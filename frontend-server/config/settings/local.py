"""
Local development — runs directly, API server at localhost:8000.
"""
from .base import *  # noqa: F401,F403

DEBUG = True
API_SERVER_URL = "http://localhost:8000"
