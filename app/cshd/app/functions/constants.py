""" Constants

"""

MAIN_FOLDER: str = "/cshd/"

ILLEGAL_DIR_CHARS: str = '<>?:"\\|?*,'

# Functions within django app
FUNCTIONS_APP: str = f"{ MAIN_FOLDER }app/cshd/app/functions/"


# For mkdocs_control
TIME_INTERVAL: float = 0.1
MAX_WAIT: int = 100


# For mkDocs
MKDOCS: str = f"{ MAIN_FOLDER }mkdocs/"
MKDOCS_DOCS: str = f"{ MKDOCS }docs/"
MKDOCS_TEMPLATES: str = f"{ MKDOCS }templates/"
MKDOCS_PLACEHOLDER_YML: str = f"{ MKDOCS_DOCS }placeholders.yml"


# .env manipulation
ENV_PATH = f"{ MAIN_FOLDER }.env"


# Testing
TESTING_MKDOCS: str = f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs/"
TESTING_MKDOCS_DOCS: str = f"{ TESTING_MKDOCS }docs/"
TESTING_MKDOCS_TEMPLATES: str = f"{ TESTING_MKDOCS }templates/"
TESTING_MKDOCS_PLACEHOLDERS_YAML: str = (
    f"{ TESTING_MKDOCS }docs/placeholders.yml"
)

TESTING_MKDOCS_NO_DOCS_FOLDER: str = (
    f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs_no_docs_folder/"
)
TESTING_MKDOCS_NO_TEMPLATES_FOLDER: str = (
    f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs_no_template_folder/"
)
TESTING_MKDOCS_EMPTY_FOLDERS: str = (
    f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs_empty_folders/"
)
