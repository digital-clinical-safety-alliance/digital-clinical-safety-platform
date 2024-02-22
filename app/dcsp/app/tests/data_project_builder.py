from ..models import ViewAccess

REPO_INPUTS_1 = {
    "setup_choice": "import",
    "external_repository_username_import": "username",
    "external_repository_password_token_import": "password",
    "external_repository_url_import": "url",
}

REPO_INPUTS_2 = {
    "repository_type": "github",
    "project_name": "A project name",
    "description": "A description",
    "access": ViewAccess.PUBLIC,
    "members": [1],
    "groups": [1],
}
