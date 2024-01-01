from dcsp.settings import *

import app.functions.constants as c

DEBUG = False
ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
GITHUB_REPO = c.TESTING_GITHUB_REPO
MKDOCS_LOCATION = c.TESTING_MKDOCS
MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
TESTING = True
START_AFRESH = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",  # This is where you put the name of the db file.
        # If one doesn't exist, it will be created at migration time.
    }
}
