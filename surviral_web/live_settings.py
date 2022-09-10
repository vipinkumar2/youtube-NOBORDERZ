import os
from .settings import *


DEBUG = True

ALLOWED_HOSTS = ["*"]
# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("LIVE_SURVIRAL_DATABASE_NAME"),
        "USER": os.environ.get("LIVE_SURVIRAL_DATABASE_USER"),
        "PASSWORD": os.environ.get("LIVE_SURVIRAL_DATABASE_PASSWORD"),
        "HOST": os.environ.get("LIVE_DATABASE_HOST", "localhost"),
        "PORT": os.environ.get("DATABASE_PORT", ""),
    }
}
