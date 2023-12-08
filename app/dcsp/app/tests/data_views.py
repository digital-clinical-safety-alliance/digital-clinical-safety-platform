INSTALLATION_POST_GOOD_DATA = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "email_SA": "john.doe@domain.com",
    "github_token_SA": "a token",
    "github_organisation_SA": "an organisation",
    "github_repo_SA": "www.somesite.com",
}

INSTALLATION_POST_BAD_DATA = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "email_SA": "john.doe@domain.com",
    "github_token_SA": "a token",
    "github_organisation_SA": "an organisation",
    "github_repo_SA": "www.somesite .com",
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
}

STD_CONTEXT_SETUP_1 = {
    "START_AFRESH": True,
    "mkdoc_running": False,
    "docs_available": False,
}

STD_CONTEXT_SETUP_2 = {
    "START_AFRESH": True,
    "mkdoc_running": False,
    "docs_available": True,
}

STD_CONTEXT_SETUP_3 = {
    "START_AFRESH": True,
    "mkdoc_running": True,
    "docs_available": True,
}

START_AFRESH_SETUP_3 = "GITHUB_USERNAME='a username'\nEMAIL='john.doe@domain.com'\nGITHUB_ORGANISATION='an organisation'\nGITHUB_REPO='www.somesite.com'\nGITHUB_TOKEN='a token'\nsetup_step='3'\n"

ISSUE_NUMBER_CURRENT = 6
ISSUE_NUMBER_NONEXISTENT = 1

HAZARD_COMMENT_DATA = {"comment": "comment"}
