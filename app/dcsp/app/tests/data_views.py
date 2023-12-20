import app.functions.constants as c

INSTALLATION_POST_STAND_ALONE_DATA_GOOD = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "email_SA": "john.doe@domain.com",
    "github_token_SA": "a token",
    "github_organisation_SA": "an organisation",
    "github_repo_SA": "www.somesite.com",
    "code_location_I": "",
}
INSTALLATION_POST_STAND_ALONE_DATA_BAD = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "email_SA": "john.doe@domain.com",
    "github_token_SA": "a token",
    "github_organisation_SA": "an organisation",
    "github_repo_SA": "a_bad[space] website.com",
    "code_location_I": "",
}

INSTALLATION_POST_INTEGRATED_DATA_GOOD = {
    "installation_type": "I",
    "github_username_SA": "",
    "email_SA": "",
    "github_token_SA": "",
    "github_organisation_SA": "",
    "github_repo_SA": "",
    "code_location_I": "/a_directory/",
}

INSTALLATION_POST_INTEGRATED_DATA_BAD = {
    "installation_type": "I",
    "github_username_SA": "",
    "email_SA": "",
    "github_token_SA": "",
    "github_organisation_SA": "",
    "github_repo_SA": "",
    "code_location_I": "/a_directory[space] /",
}

TEMPLATE_GOOD_DATA = {"template_choice": "test_templates"}

TEMPLATE_BAD_DATA = {"template_choice": "wrong_template"}

PLACEHOLDERS_GOOD_DATA = {
    "name_of_app": "The App",
    "lead_contact": "Mr Smith",
    "another_word_for_product": "Software",
    "first_name": "Bob",
    "surname": "Smith",
    "another_lead_contact": "Mr Jones",
    "todays_date": "01/01/2025",
}

MD_EDIT_GOOD_DATA = {"md_text": "Some test data here {{ name_of_app }}"}

MD_SAVED_GOOD_DATA = {
    "document_name": "test_template1.md",
    "md_text": "Some test data here {{ name_of_app }}",
}

MD_SAVED_BAD_FILENAME = {
    "document_name": "wrong_filename.md",
    "md_text": "Some test data here {{ name_of_app }}",
}

MD_SAVED_TEMPLATE_FILE_PATH = (
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs/docs/test_template1.md"
)

STD_CONTEXT_SETUP_NONE = {
    "START_AFRESH": True,
    "mkdoc_running": False,
    "docs_available": False,
    "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
}

STD_CONTEXT_SETUP_1 = {
    "START_AFRESH": True,
    "mkdoc_running": False,
    "docs_available": False,
    "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
}

STD_CONTEXT_SETUP_2 = {
    "START_AFRESH": True,
    "mkdoc_running": False,
    "docs_available": True,
    "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
}

STD_CONTEXT_SETUP_3 = {
    "START_AFRESH": True,
    "mkdoc_running": True,
    "docs_available": True,
    "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
}

START_AFRESH_SETUP_3 = "GITHUB_USERNAME='a username'\nEMAIL='john.doe@domain.com'\nGITHUB_ORGANISATION='an organisation'\nGITHUB_REPO='www.somesite.com'\nGITHUB_TOKEN='a token'\nsetup_step='3'\n"

ISSUE_NUMBER_CURRENT = 6
ISSUE_NUMBER_NONEXISTENT = 1

HAZARD_COMMENT_DATA = {"comment": "comment"}

CREDENTIALS_CHECK_REPO_EXISTS = {
    "github_username_exists": True,
    "github_organisation_exists": True,
    "repo_exists": True,
    "permission": "admin",
}
