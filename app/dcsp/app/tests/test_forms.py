"""Testing of forms

    NB: Not built for asynchronous testing

"""

from django.test import TestCase, tag, override_settings
from django.conf import settings

import sys

import app.functions.constants as c

"""settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
settings.GITHUB_REPO = c.TESTING_GITHUB_REPO
settings.MKDOCS_LOCATION = c.TESTING_MKDOCS
settings.MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
settings.TESTING = True
settings.START_AFRESH = True"""

sys.path.append(c.FUNCTIONS_APP)
from app.functions.docs_builder import Builder

import app.tests.data_forms as d

from app.forms import (
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    MDFileSelectForm,
    MDEditForm,
    UploadToGithubForm,
)


@tag("git")
class InstallationFormTest(TestCase):
    def test_stand_alone_data_good(self):
        pass

    def test_stand_alone_data_bad(self):
        pass

    def test_integrated_path_good(self):
        form = InstallationForm(data=d.INSTALLATION_FORM_INTEGRATED_DATA_GOOD)
        self.assertTrue(form.is_valid())

    def test_integrated_path_bad(self):
        form = InstallationForm(data=d.INSTALLATION_FORM_INTEGRATED_DATA_BAD)
        self.assertFalse(form.is_valid())


class TemplateSelectFormTest(TestCase):
    def test_template_choice_good_data(self):
        form = TemplateSelectForm(d.TEMPLATE_SELECT_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_template_choice_bad_data(self):
        form = TemplateSelectForm(d.TEMPLATE_SELECT_FORM_BAD_DATA)
        self.assertFalse(form.is_valid())


class PlaceholdersFormTest(TestCase):
    def setUp(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.copy_templates("test_templates")

    def test_good_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_BAD_DATA)
        self.assertFalse(form.is_valid())

    def tearDown(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()


class MDFileSelectFormTest(TestCase):
    def setUp(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.copy_templates("test_templates")

    def test_good_data(self):
        form = MDFileSelectForm(data=d.MD_FILE_SELECT_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_data(self):
        form = MDFileSelectForm(initial=d.MD_FILE_SELECT_BAD_DATA)
        self.assertFalse(form.is_valid())

    """def test_bad_path(self):
        with self.assertRaises(FileNotFoundError):
            MDFileSelectForm(
                mkdocs_path="/sss",
                initial=d.MD_FILE_SELECT_BAD_DATA,
            )"""

    def tearDown(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()
        pass


class MDEditFormTest(TestCase):
    def test_test2(self):
        form = MDEditForm(
            data={
                "document_name": "a document",
                "md_text": """---
some text
---
some more text""",
            }
        )
        self.assertTrue(form.is_valid())
