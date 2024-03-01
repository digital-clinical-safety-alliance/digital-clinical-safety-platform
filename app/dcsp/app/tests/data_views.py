import app.functions.constants as c


START_NEW_PROJECT_STEP_1_START_ANEW = {
    "setup_choice": "start_anew",
}

START_NEW_PROJECT_STEP_1_IMPORT = {
    "setup_choice": "import",
    "external_repository_url_import": "www.github.com/test",
    "external_repository_username_import": "test_username",
    "external_repository_password_token_import": "test_token",
}

START_NEW_PROJECT_STEP_1_IMPORT_WRONG_CHOICE = {
    "setup_choice": "BAD CHOICE",
    "external_repository_url_import": "www.github.com/test",
    "external_repository_username_import": "test_username",
    "external_repository_password_token_import": "test_token",
}

START_NEW_PROJECT_STEP_2 = {
    "project_name": "Test project",
    "description": "A test project",
    "access": "PU",
    "groups": ["1"],
    "members": ["1"],
}

START_NEW_PROJECT_STEP_2_START_ANEW_INPUTS = {
    "setup_choice": "start_anew",
    "project_name": "Test project",
    "description": "A test project",
    "access": "PU",
    "groups": ["1"],
    "members": ["1"],
}

START_NEW_PROJECT_STEP_2_IMPORT_INPUTS = {
    "setup_choice": "import",
    "external_repository_url_import": "www.github.com/test",
    "external_repository_username_import": "test_username",
    "external_repository_password_token_import": "test_token",
    "project_name": "Test project",
    "description": "A test project",
    "access": "PU",
    "groups": ["1"],
    "members": ["1"],
}
