INSTALLATION_POST_GOOD_DATA = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "github_token_SA": "a token",
    "github_repo_SA": "www.somesite.com",
}

INSTALLATION_POST_BAD_DATA = {
    "installation_type": "SA",
    "github_username_SA": "a username",
    "github_token_SA": "a token",
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

EDIT_MD_GOOD_DATA = {"text_md": "Some test data here {{ name_of_app }}"}
