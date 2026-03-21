"""
Local Docker development — API server reachable at http://api:8000.
"""
import os
from .base import *  # noqa: F401,F403

DEBUG = True
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://api:8000")
