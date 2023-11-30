""" Constants

"""
from enum import Enum

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
# TODO - work out why two env paths ?? for async testing?
TESTING_ENV_PATH_MKDOCS: str = (
    f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/.env"
)
TESTING_ENV_PATH_DJANGO: str = (
    f"{ MAIN_FOLDER }app/cshd/app/tests/test_django.env"
)

TESTING_MKDOCS: str = f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs/"
TESTING_MKDOCS_CONTROL: str = f"{ MAIN_FOLDER }app/cshd/app/tests/test_docs/mkdocs_testing_mkdocs_control/"
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


# git and Github
REPO_NAME: str = "clinical-safety-hazard-documentation"
ISSUE_LABELS_PATH: str = "/cshd/.github/labels.yml"
REPO_PATH_LOCAL: str = "/cshd"


class GhCredentials(Enum):
    USER = "user"
    ORG = "org"
    INVALID = "invalid"


class EnvKeys(Enum):
    GITHUB_USERNAME = "GITHUB_USERNAME"
    EMAIL = "EMAIL"
    GITHUB_ORGANISATION = "GITHUB_ORGANISATION"
    GITHUB_REPO = "GITHUB_REPO"
    GITHUB_TOKEN = "GITHUB_TOKEN"


TEMPLATE_HAZARD_COMMENT = """This Issue Template is based on the practices described in NHS Digital DCB0129/DCB0160 Clinical Safety Officer training.

### Description
A general description of the Hazard. Keep it short. Detail goes below.

### Cause
The upstream system Cause (can be multiple - use a numbered list) that results in the change to intended care.

### Effect
The change in the intended care pathway resulting from the Cause.

### Hazard
The *potential* for Harm to occur, even if it does not.

### Harm
An actual occurrence of a Hazard in the patient or clinical context. This is what we are assessing the **Severity** and **Likelihood** of.

### Possible Causes
An analysis of the Causes of the Hazard

-----

**Assignment**: Assign this Hazard to its Owner. Default owner is the Clinical Safety Officer {{ cookiecutter.clinical_safety_officer_name }}

**Labelling**: Add labels according to Severity. Likelihood and Risk Level

**Project**: Add to the Project 'Clinical Risk Management'

* Subsequent discussion can be used to mitigate the Hazard, reducing the likelihood (or less commonly reducing the severity) of the Harm.
* If Harm is reduced then you can change the labels to reflect this and reclassify the Risk Score.
* Issues can be linked to: Issues describing specific software changes, Pull Requests or Commits fixing Issues, external links, and much more supporting documentation. Aim for a comprehensive, well-evidenced, public and open discussion on risk and safety.
"""
