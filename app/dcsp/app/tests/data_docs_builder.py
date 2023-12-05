"""

"""

FILES_EXPECTED_ON_TEMPLATES_COPY = [
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs/docs/test_template1.md",
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs/docs/test_template2.md",
]

PLACEHOLDERS_EXPECTED = {
    "name_of_app": "",
    "lead_contact": "",
    "another_word_for_product": "",
    "first_name": "",
    "surname": "",
    "another_lead_contact": "",
    "todays_date": "",
}
# TODO - add _DATA to end
PLACEHOLDERS_GOOD = {
    "name_of_app": "The App",
    "lead_contact": "Mr Smith",
    "another_word_for_product": "Software",
    "first_name": "Bob",
    "surname": "Smith",
    "another_lead_contact": "Mr Jones",
    "todays_date": "01/01/2025",
}

TEST_LINTER_SINGLE_FILE = {
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/good_files/good_file1.md": {
        "overal": "pass",
        "equal_brackets": "pass",
        "equal_double_brackets": "pass",
        "placeholder_in_front_matter": "pass",
        "placeholders_half_curley_numbers": "pass",
    }
}

TEST_LINTER_FOLDER = {
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/good_files/good_file2.md": {
        "overal": "pass",
        "equal_brackets": "pass",
        "equal_double_brackets": "pass",
        "placeholder_in_front_matter": "pass",
        "placeholders_half_curley_numbers": "pass",
    },
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/good_files/good_file1.md": {
        "overal": "pass",
        "equal_brackets": "pass",
        "equal_double_brackets": "pass",
        "placeholder_in_front_matter": "pass",
        "placeholders_half_curley_numbers": "pass",
    },
}

TEST_LINTER_SINGLE_FILE_BAD = {
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/bad_files/bad_file1.md": {
        "overal": "fail",
        "equal_brackets": "fail",
        "equal_double_brackets": "fail",
        "placeholder_in_front_matter": "pass",
        "placeholders_half_curley_numbers": "fail",
    }
}


TEST_LINTER_FOLDER_BAD = {
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/bad_files/bad_file1.md": {
        "overal": "fail",
        "equal_brackets": "fail",
        "equal_double_brackets": "fail",
        "placeholder_in_front_matter": "pass",
        "placeholders_half_curley_numbers": "fail",
    },
    "/dcsp/app/dcsp/app/tests/test_docs/mkdocs_linter/bad_files/bad_file2.md": {
        "overal": "fail",
        "equal_brackets": "pass",
        "equal_double_brackets": "pass",
        "placeholder_in_front_matter": "fail",
        "placeholders_half_curley_numbers": "pass",
    },
}

PATH_BAD = "1234//1234faf345/"
