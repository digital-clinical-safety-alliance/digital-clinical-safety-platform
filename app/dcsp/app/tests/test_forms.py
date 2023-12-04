"""Testing of forms

    NB: Not built for asynchronous testing

"""

from django.test import TestCase

import sys

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.docs_builder import Builder

import app.tests.data_forms as d

from app.forms import (
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    MDFileSelect,
    MDEditForm,
)


class InstallationFormTest(TestCase):
    def test_good_url(self):
        form = InstallationForm(data=d.INSTALLATION_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_url(self):
        form = InstallationForm(data=d.INSTALLATION_FORM_BAD_DATA)
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
        pass

    def test_good_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_BAD_DATA)
        self.assertFalse(form.is_valid())

    def tearDown(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()


class MDFileSelectTest(TestCase):
    def setUp(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.copy_templates("test_templates")

    def test_good_data(self):
        form = MDFileSelect(data=d.MD_FILE_SELECT_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_data(self):
        form = MDFileSelect(initial=d.MD_FILE_SELECT_BAD_DATA)
        self.assertFalse(form.is_valid())

    """def test_bad_path(self):
        with self.assertRaises(FileNotFoundError):
            MDFileSelect(
                mkdocs_path="/sss",
                initial=d.MD_FILE_SELECT_BAD_DATA,
            )"""

    def tearDown(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()
        pass


"""class MDEditFormTest(TestCase):
    def test_test2(self):
        form = MDEditForm(data={})
        self.assertTrue(form.is_valid())"""
