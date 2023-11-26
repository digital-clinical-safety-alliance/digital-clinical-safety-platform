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

PLACEHOLDERS_FORM_GOOD_DATA = {
    "name_of_app": "",
    "lead_contact": "",
    "another_word_for_product": "",
    "first_name": "",
    "surname": "",
    "another_lead_contact": "",
    "todays_date": "",
}

PLACEHOLDERS_FORM_BAD_DATA = {
    "name_of_app": "{",
    "lead_contact": "",
    "another_word_for_product": "",
    "first_name": "",
    "surname": "",
    "another_lead_contact": "",
    "todays_date": "",
}

TEMPLATE_SELECT_FORM_GOOD_DATA = {"template_choice": "test_templates"}

TEMPLATE_SELECT_FORM_BAD_DATA = {"template_choice": "DCB0111"}

MD_FILE_SELECT_GOOD_DATA = {"mark_down_file": "test_template1.md"}

MD_FILE_SELECT_BAD_DATA = {
    "mark_down_file": "made_up_file.md",
}


MD_EDIT_FORM_GOOD_DATA = {}
