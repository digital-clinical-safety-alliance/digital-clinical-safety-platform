"""

"""

FILES_EXPECTED_ON_TEMPLATES_COPY = [
    "/cshd/app/cshd/app/tests/test_docs/mkdocs/docs/test_template1.md",
    "/cshd/app/cshd/app/tests/test_docs/mkdocs/docs/test_template2.md",
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
