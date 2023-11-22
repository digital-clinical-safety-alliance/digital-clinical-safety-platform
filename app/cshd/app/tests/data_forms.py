"""Test data for testing"""

INSTALLATION_FORM_GOOD_DATA = {
    "installation_type": "SA",
    "github_repo_SA": "aaaf",
    "github_username_SA": "a",
    "github_token_SA": "x",
    "code_location_I": "s",
}

INSTALLATION_FORM_BAD_DATA = {
    "installation_type": "SA",
    "github_repo_SA": "aaaf l",
    "github_username_SA": "a",
    "github_token_SA": "x",
    "code_location_I": "s",
}

PLACEHOLDERS_FORM_GOOD_DATA = {"project_name": "Super Project"}

PLACEHOLDERS_FORM_BAD_DATA = {"project_name": "{ljklkj"}

TEMPLATE_SELECT_FORM_GOOD_DATA = {"template_choice": "DCB0129"}

TEMPLATE_SELECT_FORM_BAD_DATA = {"template_choice": "DCB0111"}

MD_FILE_SELECT_GOOD_DATA = {
    "mark_down_file": "hazard-log.md",
}

MD_FILE_SELECT_BAD_DATA = {
    "mark_down_file": "made_up_file.md",
}


MD_EDIT_FORM_GOOD_DATA = {}
