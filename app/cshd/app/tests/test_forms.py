"""Testing of forms

"""

from django.test import TestCase


import os
from fnmatch import fnmatch
import sys


import app.functions.constants as c

"""sys.path.append(c.FUNCTIONS_APP)
from docs_builder import Builder"""

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
        form = TemplateSelectForm(data=d.TEMPLATE_SELECT_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_template_choice_bad_data(self):
        form = TemplateSelectForm(data=d.TEMPLATE_SELECT_FORM_BAD_DATA)
        self.assertFalse(form.is_valid())


class PlaceholdersFormTest(TestCase):
    def test_good_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_placeholder(self):
        form = PlaceholdersForm(data=d.PLACEHOLDERS_FORM_BAD_DATA)
        self.assertFalse(form.is_valid())


class MDFileSelectTest(TestCase):
    def test_good_data(self):
        form = MDFileSelect(data=d.MD_FILE_SELECT_GOOD_DATA)
        self.assertTrue(form.is_valid())

    def test_bad_data(self):
        form = MDFileSelect(data=d.MD_FILE_SELECT_BAD_DATA)
        self.assertFalse(form.is_valid())


class MDEditFormTest(TestCase):
    def test_test2(self):
        form = MDEditForm(data={})
        self.assertTrue(form.is_valid())
