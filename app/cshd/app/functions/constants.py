""" Constants

"""

MAIN_FOLDER: str = "/cshd/"

# Functions within django app
FUNCTIONS_APP: str = f"{ MAIN_FOLDER }app/cshd/app/functions/"


# For mkdocs_control
TIME_INTERVAL: float = 0.1
MAX_WAIT: int = 100


# For mkDocs
MKDOCS: str = f"{ MAIN_FOLDER }mkdocs/"
MKDOCS_DOCS: str = f"{ MKDOCS }docs/"
MKDOCS_TEMPLATES: str = f"{ MKDOCS }templates/"

# .env manipulation
ENV_PATH = f"{ MAIN_FOLDER }.env"
