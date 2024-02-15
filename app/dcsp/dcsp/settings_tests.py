from dcsp.settings import *

import app.functions.constants as c

DEBUG = False
ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
GITHUB_REPO = c.TESTING_GITHUB_REPO
MKDOCS_LOCATION = c.TESTING_MKDOCS
MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
TESTING = True

# TODO - need to work out if this is okay for testing on GHA
DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "POSTGRES_ENGINE",
            "django.db.backends.sqlite3",
        ),
        "NAME": "dcsp-postgres-cicd",  # os.environ.get("POSTGRES_DB", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": "dcsp-postgres-cicd",  # os.environ.get("POSTGRES_HOST", "dcsp-postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
