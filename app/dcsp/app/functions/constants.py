""" Constants

Forward slash '/' is placed at the end of directory names
"""
from enum import Enum

MAIN_FOLDER: str = "/dcsp/"

TEMPLATES_FOLDER: str = "/dcsp/app/dcsp/app/templates/"


TESTS_LOCATION: str = f"{ MAIN_FOLDER }app/dcsp/app/tests/"

ILLEGAL_DIR_CHARS: str = '<>?:"\\|?*,'

# Functions within django app
FUNCTIONS_APP: str = f"{ MAIN_FOLDER }app/dcsp/app/functions/"

# Project path related
PROJECTS_FOLDER: str = "/projects/"
# START_AFRESH_PARENT_FOLDER: str = "src/"
CLINICAL_SAFETY_FOLDER: str = "CS-documents/"
HAZARDS_SUMMARY_FILE: str = "hazards-summary.md"

# For mkdocs_control
TIME_INTERVAL: float = 0.1
MAX_WAIT: int = 100


# For mkDocs
MKDOCS: str = f"{ MAIN_FOLDER }mkdocs/"
MKDOCS_DOCS: str = f"{ MKDOCS }docs/"
MKDOCS_TEMPLATES: str = f"{ MKDOCS }templates/"
MKDOCS_PLACEHOLDER_YML: str = f"{ MKDOCS_DOCS }placeholders.yml"

# .env
ENV_PATH = f"{ MAIN_FOLDER }.env"


# .env manipulation for placeholders
ENV_PATH_PLACEHOLDERS = f"{ MAIN_FOLDER }.env_placeholders"


# Testing MKDOCS
# TODO - work out why two env paths ?? for async testing?
TESTING_ENV_PATH_MKDOCS: str = (
    f"{ TESTS_LOCATION }test_docs/.env_placeholders_test"
)


TESTING_MKDOCS: str = f"{ TESTS_LOCATION }test_docs/mkdocs/"
TESTING_MKDOCS_CONTROL: str = (
    f"{ TESTS_LOCATION }test_docs/mkdocs_testing_mkdocs_control/"
)
TESTING_MKDOCS_DOCS: str = f"{ TESTING_MKDOCS }docs/"
TESTING_MKDOCS_TEMPLATES: str = f"{ TESTING_MKDOCS }templates/"
TESTING_MKDOCS_PLACEHOLDERS_YAML: str = (
    f"{ TESTING_MKDOCS }docs/placeholders.yml"
)

TESTING_MKDOCS_NO_DOCS_FOLDER: str = (
    f"{ TESTS_LOCATION }test_docs/mkdocs_no_docs_folder/"
)
TESTING_MKDOCS_NO_TEMPLATES_FOLDER: str = (
    f"{ TESTS_LOCATION }test_docs/mkdocs_no_template_folder/"
)
TESTING_MKDOCS_EMPTY_FOLDERS: str = (
    f"{ TESTS_LOCATION }test_docs/mkdocs_empty_folders/"
)
TESTING_MKDOCS_LINTER: str = f"{ TESTS_LOCATION }test_docs/mkdocs_linter/"
TESTING_MKDOCS_LINTER_DOCS: str = f"{ TESTING_MKDOCS_LINTER }docs/"
# testing Django
TESTING_ENV_PATH_DJANGO: str = (
    f"{ TESTS_LOCATION }test_django/.env_placeholders_test"
)

# git and Github
REPO_NAME: str = "digital-clinical-safety-platform"
ISSUE_LABELS_PATH: str = "/dcsp/app/dcsp/app/functions/labels.yml"
REPO_PATH_LOCAL: str = "/dcsp"

TESTING_GITHUB_REPO = "test-repo-exists"
TESTING_CURRENT_ISSUE = 220


class GhCredentials(Enum):
    USER = "user"
    ORG = "org"
    INVALID = "invalid"


class EnvKeys(Enum):
    DJANGO_SECRET_KEY = "DJANGO_SECRET_KEY"  # nosec B105
    ALLOW_HOSTS = "ALLOW_HOSTS"
    DOCKERHUB_USERNAME = "DOCKERHUB_USERNAME"
    DOCKERHUB_PASSWORD = "DOCKERHUB_PASSORD"  # nosec B105


# Placeholder env keys
class EnvKeysPH(Enum):
    GITHUB_USERNAME = "GITHUB_USERNAME"
    EMAIL = "EMAIL"
    GITHUB_ORGANISATION = "GITHUB_ORGANISATION"
    GITHUB_REPO = "GITHUB_REPO"
    GITHUB_TOKEN = "GITHUB_TOKEN"  # nosec B105


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

# Testing git and GitHub
TESTING_ENV_PATH_GIT_DIR_ONLY: str = f"{ TESTS_LOCATION }git_control/"
TESTING_ENV_PATH_GIT: str = (
    f"{ TESTS_LOCATION }git_control/.env_placeholders_test"
)

FORM_ELEMENTS_MAX_WIDTH: str = "max-w-800"

# TODO might have to remove 'map'
MIME_TYPES = {
    "map": "application/json",
    "html": "text/html",
    "htm": "text/html",
    "shtml": "text/html",
    "css": "text/css",
    "xml": "text/xml",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "js": "application/javascript",
    "atom": "application/atom+xml",
    "rss": "application/rss+xml",
    "mml": "text/mathml",
    "txt": "text/plain",
    "jad": "text/vnd.sun.j2me.app-descriptor",
    "wml": "text/vnd.wap.wml",
    "htc": "text/x-component",
    "avif": "image/avif",
    "png": "image/png",
    "svg": "image/svg+xml",
    "svgz": "image/svg+xml",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "wbmp": "image/vnd.wap.wbmp",
    "webp": "image/webp",
    "ico": "image/x-icon",
    "jng": "image/x-jng",
    "bmp": "image/x-ms-bmp",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "jar": "application/java-archive",
    "war": "application/java-archive",
    "ear": "application/java-archive",
    "json": "application/json",
    "hqx": "application/mac-binhex40",
    "doc": "application/msword",
    "pdf": "application/pdf",
    "ps": "application/postscript",
    "eps": "application/postscript",
    "ai": "application/postscript",
    "rtf": "application/rtf",
    "m3u8": "application/vnd.apple.mpegurl",
    "kml": "application/vnd.google-earth.kml+xml",
    "kmz": "application/vnd.google-earth.kmz",
    "xls": "application/vnd.ms-excel",
    "eot": "application/vnd.ms-fontobject",
    "ppt": "application/vnd.ms-powerpoint",
    "odg": "application/vnd.oasis.opendocument.graphics",
    "odp": "application/vnd.oasis.opendocument.presentation",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "odt": "application/vnd.oasis.opendocument.text",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "wmlc": "application/vnd.wap.wmlc",
    "wasm": "application/wasm",
    "7z": "application/x-7z-compressed",
    "cco": "application/x-cocoa",
    "jardiff": "application/x-java-archive-diff",
    "jnlp": "application/x-java-jnlp-file",
    "run": "application/x-makeself",
    "pl": "application/x-perl",
    "pm": "application/x-perl",
    "prc": "application/x-pilot",
    "pdb": "application/x-pilot",
    "rar": "application/x-rar-compressed",
    "rpm": "application/x-redhat-package-manager",
    "sea": "application/x-sea",
    "swf": "application/x-shockwave-flash",
    "sit": "application/x-stuffit",
    "tcl": "application/x-tcl",
    "tk": "application/x-tcl",
    "der": "application/x-x509-ca-cert",
    "pem": "application/x-x509-ca-cert",
    "crt": "application/x-x509-ca-cert",
    "xpi": "application/x-xpinstall",
    "xhtml": "application/xhtml+xml",
    "xspf": "application/xspf+xml",
    "zip": "application/zip",
    "bin": "application/octet-stream",
    "exe": "application/octet-stream",
    "dll": "application/octet-stream",
    "deb": "application/octet-stream",
    "dmg": "application/octet-stream",
    "iso": "application/octet-stream",
    "img": "application/octet-stream",
    "msi": "application/octet-stream",
    "msp": "application/octet-stream",
    "msm": "application/octet-stream",
    "mid": "audio/midi",
    "midi": "audio/midi",
    "kar": "audio/midi",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "m4a": "audio/x-m4a",
    "ra": "audio/x-realaudio",
    "3gpp": "video/3gpp",
    "3gp": "video/3gpp",
    "ts": "video/mp2t",
    "mp4": "video/mp4",
    "mpeg": "video/mpeg",
    "mpg": "video/mpeg",
    "mov": "video/quicktime",
    "webm": "video/webm",
    "flv": "video/x-flv",
    "m4v": "video/x-m4v",
    "mng": "video/x-mng",
    "asx": "video/x-ms-asf",
    "asf": "video/x-ms-asf",
    "wmv": "video/x-ms-wmv",
    "avi": "video/x-msvideo",
}
